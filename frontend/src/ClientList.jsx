// ClientList.jsx

import React, { useEffect, useState } from "react";

function ClientList() {
  const [clients, setClients] = useState([]);

  // This useEffect hook now fetches data every 5 seconds.
  useEffect(() => {
    const fetchData = () => {
      console.log("Fetching latest client data..."); // For debugging
      fetch("http://localhost:8000/clients")
        .then((res) => res.json())
        .then((data) => setClients(data))
        .catch(err => console.error("Failed to fetch client data:", err));
    };

    fetchData(); // Fetch data immediately when the component loads

    const intervalId = setInterval(fetchData, 5000); // Set up polling every 5 seconds

    // This is a cleanup function that stops the polling when you navigate away.
    // It's important for preventing errors and memory leaks.
    return () => clearInterval(intervalId);
  }, []); // The empty array ensures this effect runs only once to set up the interval.

  const markAsRead = (client_id) => {
    fetch(`http://localhost:8000/mark-read/${client_id}`, { method: "POST" })
      .then(() => {
        // After marking as read, optimistically update the UI immediately
        // instead of waiting for the next 5-second poll.
        setClients((prev) =>
          prev.map((client) =>
            client["Client ID"] === client_id
              ? { ...client, unread_count: 0 }
              : client
          )
        );
      });
  };

  const getStatusDisplay = (client) => {
    if (client.unread_count > 0) {
      const mailText = client.unread_count === 1 ? "Unread Mail" : "Unread Mails";
      return `🔴 ${client.unread_count} ${mailText}`;
    }
    if (client.mail_date) {
      return "✅ All Read";
    }
    return "📭 No Mail History";
  };

  return (
    <div style={{ marginTop: "30px", padding: "20px" }}>
      <h2>📋 Client Mail Tracker</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "10px" }}>
        <thead>
          <tr style={{ background: "#f0f0f0" }}>
            <th style={thStyle}>Client ID</th>
            <th style={thStyle}>Client Name</th>
            <th style={thStyle}>Branch</th>
            <th style={thStyle}>Mail Status</th>
            <th style={thStyle}>Mail Date</th>
            <th style={thStyle}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr key={client["Client ID"]}>
              <td style={tdStyle}>{client["Client ID"]}</td>
              <td style={tdStyle}>{client["Client Name"] || "--"}</td>
              <td style={thStyle}>{client["Branch Name"] || "--"}</td>
              <td style={tdStyle}>{getStatusDisplay(client)}</td>
              <td style={tdStyle}>{client.mail_date || "--"}</td>
              <td style={tdStyle}>
                <button
                  onClick={() =>
                    window.open(`http://localhost:8000/download/${client["Client ID"]}`, "_blank")
                  }
                  style={btnStyle}
                >
                  📁 Download Zip
                </button>
                {client.unread_count > 0 && (
                  <button onClick={() => markAsRead(client["Client ID"])} style={btnStyle}>
                    ✅ Mark All Read
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {clients.length === 0 && (
        <p style={{ marginTop: "20px", color: "gray" }}>No client records to show.</p>
      )}
    </div>
  );
}

const thStyle = {
  padding: "10px",
  border: "1px solid #ccc",
  textAlign: "left",
};

const tdStyle = {
  padding: "10px",
  border: "1px solid #ccc",
};

const btnStyle = {
  padding: "6px 10px",
  marginRight: "6px",
  backgroundColor: "#e0e0e0",
  border: "none",
  borderRadius: "4px",
  cursor: "pointer",
};

export default ClientList;