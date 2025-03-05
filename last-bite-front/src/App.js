import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
    const [data, setData] = useState("");

    useEffect(() => {
        axios.get(`${process.env.REACT_APP_API_URL}/data`)
            .then(response => setData(response.data.message))
            .catch(error => console.error("Error fetching data:", error));
    }, []);

    return (
        <div>
            <h1>Flask + React</h1>
            <p>{data || "Loading..."}</p>
        </div>
    );
}

export default App;
