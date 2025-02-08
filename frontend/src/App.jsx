import React from "react";
import FileUpload from "./FileUpload";
import "./App.css"; // For styling

function App() {
    return (
        <div className="app-container">
            <h1>Rent Agreement Analyzer</h1>
            <FileUpload />
        </div>
    );
}

export default App;