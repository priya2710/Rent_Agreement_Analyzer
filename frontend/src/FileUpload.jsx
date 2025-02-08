import React, { useState } from "react";
import axios from "axios";
import "./FileUpload.css"; // For styling

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showAlert, setShowAlert] = useState(false);

    // Handle file selection
    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    // Handle file upload
    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file.");
            setShowAlert(true);
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {
            setLoading(true); // Show loading
            const res = await axios.post("http://127.0.0.1:8000/upload/", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setResponse(res.data);
            setError(null);
        } catch (err) {
            setError("Error uploading file. Please try again.");
            setShowAlert(true);
            console.error(err);
        } finally {
            setLoading(false); // Hide loading
        }
    };

    // Handle alert box "OK" button click (reloads page)
    const handleAlertClose = () => {
        setShowAlert(false);
        window.location.reload();
    };

    return (
        <div className="file-upload-container">
            <h2>Upload Rent Agreement</h2>

            {/* File Input */}
            <input type="file" onChange={handleFileChange} accept="application/pdf" />

            {/* Upload Button */}
            <button onClick={handleUpload}>Upload</button>

            {/* Loading Screen */}
            {loading && (
                <div className="loading-overlay">
                    <div className="loading-spinner"></div>
                    <p>Processing file, please wait...</p>
                </div>
            )}

            {/* Error Alert Box */}
            {showAlert && (
                <div className="alert-box">
                    <p>{error}</p>
                    <button onClick={handleAlertClose}>OK</button>
                </div>
            )}

            {/* Response Section */}
            {response && (
                <div className="response-container">
                    <h3>Conflicting Clauses </h3>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Clause 1</th>
                                <th>Clause 2</th>
                                <th>Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                            {response.contradictions.map((contradiction, index) => (
                                <tr key={index}>
                                    <td>{index + 1}</td>
                                    <td>{contradiction["Clause 1"]}</td>
                                    <td>{contradiction["Clause 2"]}</td>
                                    <td>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{ width: `${contradiction.Confidence * 100}%` }}
                                            ></div>
                                            <span>{(contradiction.Confidence * 100).toFixed(2)}%</span>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default FileUpload;