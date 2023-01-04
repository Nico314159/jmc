from pathlib import Path
from typing import Callable

from .utils import is_connected
from .header import Header, MacroFactory
from .tokenizer import Token, TokenType, Tokenizer
from .exception import HeaderDuplicatedMacro, HeaderFileNotFoundError, HeaderSyntaxException, JMCSyntaxException
from .log import Logger

logger = Logger(__name__)


def __empty_macro_factory(
        argument_tokens: list[Token], line: int, col: int) -> list[Token]:
    return []


def __copy_macro_token(token: Token, line: int, col: int,
                       length: int, replaced_token_col: int, token_col: int | None = None) -> Token:
    if token_col is None:
        token_col = token.col
    return Token(token.token_type, line=line, col=col + token_col - replaced_token_col,
                 string=token.string, _macro_length=length)


def __create_macro_factory(
        replaced_tokens: list[Token], parameters_token: Token | None, key: str, tokenizer: Tokenizer, error: HeaderSyntaxException) -> tuple[MacroFactory, int]:
    if not replaced_tokens:
        return __empty_macro_factory, 0

    # Parsing parameters_token
    parameter_tokens: list[Token] = []
    if parameters_token is not None:
        parameter_tokens_, invalid_kwargs = tokenizer.parse_func_args(
            parameters_token)
        for parameter_token_ in parameter_tokens_:
            if parameter_token_[0].token_type != TokenType.KEYWORD:
                raise JMCSyntaxException(
                    f"Macro factory arguments can only have a keyword token (got {parameter_token_[0].token_type})", parameter_token_[0], tokenizer)
            if len(parameter_token_) > 1:
                raise JMCSyntaxException(
                    f"Macro factory arguments can only have 1 token each (got {len(parameter_token_)})", parameter_token_[1], tokenizer)
            parameter_tokens.append(parameter_token_[0])
        if invalid_kwargs:
            raise error

    # Creating template
    template_tokens: list[Token | tuple[int, Token]] = []
    replaced_token_col = replaced_tokens[0].col
    for token in replaced_tokens:
        for index, parameter_token in enumerate(parameter_tokens):
            if token.token_type == parameter_token.token_type and token.string == parameter_token.string:
                template_tokens.append((index, token))
                break
        else:
            template_tokens.append(token)

    def macro_factory(
            argument_tokens: list[Token], line: int, col: int) -> list[Token]:

        return_list: list[Token] = []
        extra_col = 0
        for token_or_int in template_tokens:
            if isinstance(token_or_int, Token):
                return_list.append(
                    __copy_macro_token(
                        token_or_int, line, col +
                        extra_col, len(key), replaced_token_col
                    )
                )
            else:
                return_list.append(
                    __copy_macro_token(
                        argument_tokens[token_or_int[0]],
                        line,
                        col,
                        len(key),
                        replaced_token_col,
                        token_or_int[1].col
                    )
                )
                extra_col += argument_tokens[token_or_int[0]
                                             ].length - token_or_int[1].length

        return return_list
    return macro_factory, len(parameter_tokens)


def __parse_header(header_str: str, file_name: str,
                   parent_target: Path, namespace_path: Path) -> Header:
    header = Header()
    lines = header_str.split("\n")
    for line, line_str in enumerate(lines):
        line += 1
        if line_str.isspace() or line_str.startswith("//") or line_str == "":
            continue

        if not line_str.startswith("#"):
            raise HeaderSyntaxException(
                "Expected '#' at the start of the line", file_name, line, line_str)

        if line_str == "#":
            raise HeaderSyntaxException(
                "Expected directive after '#'", file_name, line, line_str)

        tokenizer = Tokenizer(
            line_str[1:], file_name, line=line, col=2, expect_semicolon=False, file_string=header_str)
        directive_and_args = tokenizer.programs[0]
        directive_token = directive_and_args[0]
        arg_tokens = directive_and_args[1:]
        if directive_token.token_type != TokenType.KEYWORD:
            raise HeaderSyntaxException(
                f"Expected directive(keyword) after '#' (got {directive_token.token_type.value})", file_name, line, line_str)

        # #define
        if directive_token.string == "define":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    "Expected keyword after '#define'", file_name, line, line_str)

            key = arg_tokens[0].string
            if key in header.macros:
                raise HeaderDuplicatedMacro(
                    f"'{key}' macro is already defined", file_name, line, line_str)

            if len(arg_tokens) == 1:
                #  #define KEYWORD
                header.macros[key] = (__empty_macro_factory, 0)

            elif arg_tokens[1].token_type == TokenType.PAREN_ROUND and is_connected(
                    arg_tokens[1], arg_tokens[0]):
                #  #define KEYWORD(arg1, arg2)
                header.macros[key] = __create_macro_factory(
                    arg_tokens[2:], arg_tokens[1], key, tokenizer, HeaderSyntaxException(
                        "Invalid marcro argument syntax", file_name, line, line_str))
            else:
                #  #define KEYWORD TOKEN
                header.macros[key] = __create_macro_factory(
                    arg_tokens[1:], None, key, tokenizer, HeaderSyntaxException(
                        "Invalid marcro argument syntax", file_name, line, line_str))

                # #include
        elif directive_token.string == "include":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected included file name(string) after '#include'", file_name, line, line_str)
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#include' (got {len(arg_tokens)})", file_name, line, line_str)
            new_file_name = arg_tokens[0].string
            if not new_file_name.endswith(".hjmc"):
                new_file_name += ".hjmc"
            header_file = parent_target / new_file_name
            if not header_file.is_file():
                raise HeaderFileNotFoundError(header_file)
            with header_file.open("r") as file:
                header_str = file.read()
            logger.info(f"Parsing {header_file}")
            if header.is_header_exist(header_file):
                raise HeaderSyntaxException(
                    f"File {header_file.as_posix()} is already included.", file_name, line, line_str)
            header.add_file_read(header_file)
            __parse_header(
                header_str,
                header_file.as_posix(),
                parent_target,
                namespace_path)

        # #credit
        elif directive_token.string == "credit":
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 0-1 arguments after '#credit' (got {len(arg_tokens)})", file_name, line, line_str)
            if arg_tokens:
                if arg_tokens[0].token_type != TokenType.STRING:
                    raise HeaderSyntaxException(
                        "Expected included file name(string) after '#include'", file_name, line, line_str)
                header.credits.append(arg_tokens[0].string)
            else:
                header.credits.append("")

        # #override_minecraft
        elif directive_token.string == "override_minecraft":
            if arg_tokens:
                raise HeaderSyntaxException(
                    f"Expected 0 arguments after '#override_minecraft' (got {len(arg_tokens)})", file_name, line, line_str)
            header.is_override_minecraft = True

        # #command
        elif directive_token.string == "command":
            if not arg_tokens or len(arg_tokens) != 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#command' (got {len(arg_tokens)})", file_name, line, line_str)
            if arg_tokens[0].token_type != TokenType.KEYWORD:
                raise HeaderSyntaxException(
                    f"Expected keyword after '#command' (got {arg_tokens[0].token_type.value})", file_name, line, line_str)
            header.commands.add(arg_tokens[0].string)

        # #static
        elif directive_token.string == "static":
            if not arg_tokens or arg_tokens[0].token_type != TokenType.STRING:
                raise HeaderSyntaxException(
                    "Expected static folder name(string) after '#static'", file_name, line, line_str)
            if len(arg_tokens) > 1:
                raise HeaderSyntaxException(
                    f"Expected 1 arguments after '#static' (got {len(arg_tokens)})", file_name, line, line_str)
            static_folder = namespace_path / arg_tokens[0].string
            if not static_folder.is_dir():
                # raise JMCFileNotFoundError(
                # f"Static folder not found: {static_folder.as_posix()}\nPlease
                # recheck that the path is correct so that JMC won't
                # accidentally delete your folder.")
                raise HeaderSyntaxException(
                    f"Static folder not found: {static_folder.as_posix()}", file_name, line, line_str, suggestion="Please recheck that the path is correct so that JMC won't accidentally delete your folder.")
            header.statics.add(static_folder)
        else:
            raise HeaderSyntaxException(
                f"Unrecognized directive '{directive_token.string}'", file_name, line, line_str)

    return header


def parse_header(header_str: str, file_name: str,
                 parent_target: Path, namespace_path: Path) -> Header:
    """
    Parse header and store the information in the header object

    :param header_str: String that was read from the file
    :param file_name: Header file's name
    :param parent_target: Path to parent of the main jmc file
    :raises HeaderSyntaxException: A line in the file doesn't start with '#'
    :raises HeaderDuplicatedMacro: Define same macro twice
    :raises HeaderSyntaxException: Too many/little argument for define
    :raises HeaderSyntaxException: File name isn't wrapped in quote or angle bracket (For `#include`)
    :raises HeaderFileNotFoundError: Can't find header file
    :raises HeaderSyntaxException: Include same file twice
    :raises HeaderSyntaxException: Whitespace found in header file's name
    :raises NotImplementedError: WORKING ON `#replace`
    :raises NotImplementedError: WORKING ON `#credit`
    :raises HeaderSyntaxException: Directive (`#something`) is unrecognized
    :return: Header singleton object
    """
    header = Header()
    header.is_enable_macro = False
    return_value = __parse_header(
        header_str,
        file_name,
        parent_target,
        namespace_path)
    header.is_enable_macro = True
    return return_value