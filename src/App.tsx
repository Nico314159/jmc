import React from "react";
import {
    HashRouter as Router,
    Route,
    Routes,
    Navigate,
} from "react-router-dom";

import NavBar from "./components/Navbar";

import Home from "./pages/Home";
import Download from "./pages/Download";
import Introduction from "./pages/Introduction";
import HowItWorks from "./pages/HowItWorks";
import Installation from "./pages/Installation";
import Code from "./pages/Code";
import MultilineCommand from "./pages/MultilineCommand";
import Import from "./pages/Import";
import Comment from "./pages/Comment";
import LoadTick from "./pages/LoadTick";
import Variable from "./pages/Variable";
import FlowControls from "./pages/FlowControls";
import JsonFiles from "./pages/JsonFiles";
import BuiltInFunction from "./pages/BuiltInFunction";
import Basics from "./pages/Basics";
import Advanced from "./pages/Advanced";
import Submitted from "./pages/Submitted";

function App() {
    return (
        <Router>
            <div className="App w-screen">
                <NavBar />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/download" element={<Download />} />
                    <Route
                        path="/getting-started/introduction"
                        element={<Introduction />}
                    />
                    <Route
                        path="/getting-started/how-it-works"
                        element={<HowItWorks />}
                    />
                    <Route
                        path="/getting-started/installation"
                        element={<Installation />}
                    />
                    <Route path="/getting-started/code" element={<Code />} />

                    <Route
                        path="/documentation/multiline-command"
                        element={<MultilineCommand />}
                    />
                    <Route path="/documentation/import" element={<Import />} />
                    <Route
                        path="/documentation/comment"
                        element={<Comment />}
                    />
                    <Route
                        path="/documentation/load-tick"
                        element={<LoadTick />}
                    />
                    <Route
                        path="/documentation/variable"
                        element={<Variable />}
                    />
                    <Route
                        path="/documentation/flow-controls"
                        element={<FlowControls />}
                    />
                    <Route
                        path="/documentation/json-files"
                        element={<JsonFiles />}
                    />
                    <Route
                        path="/documentation/built-in-function"
                        element={<BuiltInFunction />}
                    />

                    <Route path="/examples/basics" element={<Basics />} />
                    <Route path="/examples/advanced" element={<Advanced />} />
                    <Route path="/examples/submitted" element={<Submitted />} />
                    <Route path="/*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
