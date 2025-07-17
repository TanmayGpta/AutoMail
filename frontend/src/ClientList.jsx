import React, { useEffect, useState } from "react";

function ClientList() {
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/unread-mails")
      .then((res) => res.json())
      .then((data) => setClients(data));
  }, []);

  const markAsRead = (client_id) => {
    fetch(`http://localhost:8000/mark-read/${client_id}`, { method: "POST" })
      .then(() => {
        setClients((prev) =>
          prev.filter((client) => client.client_id !== client_id)
        );
      });
  };

  return (
    <div style={{ marginTop: "20px" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#f0f0f0" }}>
            <th style={thStyle}>Client ID</th>
            <th style={thStyle}>Mail Status</th>
            <th style={thStyle}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {clients.map((client) => (
            <tr key={client.client_id}>
              <td style={tdStyle}>{client.client_id}</td>
              <td style={tdStyle}>
                {client.unread ? "🔴 Unread" : "✅ Read"}
              </td>
              <td style={tdStyle}>
                <button
                  onClick={() =>
                    window.open(
                      `http://localhost:8000/download/${client.client_id}`,
                      "_blank"
                    )
                  }
                  style={{ marginRight: "10px" }}
                >
                  Download Zip
                </button>
                <button onClick={() => markAsRead(client.client_id)}>
                  Mark as Read
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {clients.length === 0 && (
        <p style={{ color: "gray", marginTop: "20px" }}>
          ✅ All mails processed.
        </p>
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

export default ClientList;
