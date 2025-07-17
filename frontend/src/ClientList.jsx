import React, { useEffect, useState } from "react";

function ClientList() {
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/clients")
      .then((res) => res.json())
      .then((data) => setClients(data));
  }, []);

  const markAsRead = (client_id) => {
    fetch(`http://localhost:8000/mark-read/${client_id}`, { method: "POST" })
      .then(() => {
        setClients((prev) =>
          prev.map((client) =>
            client["Client ID"] === client_id
              ? { ...client, unread: false }
              : client
          )
        );
      });
  };

  const checkZipExists = async (client_id) => {
    try {
      const res = await fetch(
        `http://localhost:8000/download/${client_id}`,
        { method: "HEAD" }
      );
      return res.ok;
    } catch (e) {
      return false;
    }
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
              <td style={tdStyle}>{client["Branch Name"] || "--"}</td>
              <td style={tdStyle}>
                {client.unread ? "🔴 Unread" : client.mail_date ? "✅ Read" : "📭 No new mail"}
              </td>
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
                {client.unread && (
                  <button onClick={() => markAsRead(client["Client ID"])} style={btnStyle}>
                    ✅ Mark Read
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
