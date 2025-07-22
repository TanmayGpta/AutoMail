import React, { useEffect, useState } from "react";

function ClientList() {
  const [clients, setClients] = useState([]);
  const GMAIL_ACCOUNT = "predecentt@gmail.com";

  useEffect(() => {
    const fetchData = () => {
      fetch("http://localhost:8000/clients")
        .then((res) => res.json())
        .then((data) => setClients(data));
    };
    fetchData();
    const intervalId = setInterval(fetchData, 5000);
    return () => clearInterval(intervalId);
  }, []);

  const openGmail = (messageId) => {
    const url = `https://mail.google.com/mail/u/?authuser=${GMAIL_ACCOUNT}#search/rfc822msgid%3A${messageId}`;
    window.open(url, "_blank");
  };

  return (
    <div style={{ marginTop: "30px", padding: "20px" }}>
      <h2>📋 Client Mail Tracker</h2>
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "10px" }}>
        {/* Table Head is the same */}
        <tbody>
          {clients.map((client) => (
            <tr key={client["Client ID"]}>
              <td style={tdStyle}>{client["Client ID"]}</td>
              <td style={tdStyle}>{client["Client Name"] || "--"}</td>
              <td style={tdStyle}>{client["Branch Name"] || "--"}</td>
              <td style={tdStyle}>
                {client.unread_count > 0 ? (
                  <div>
                    <div style={{ fontWeight: "bold", marginBottom: "5px" }}>🔴 {client.unread_count} Unread</div>
                    <ul style={{ margin: 0, paddingLeft: "20px" }}>
                      {client.mails
                        .filter(mail => !mail.is_read)
                        .map((mail, index) => (
                          <li key={index} style={{ marginBottom: "5px" }}>
                            {mail.mail_date}
                            <button onClick={() => openGmail(mail.gmail_message_id)} style={viewBtnStyle}>View</button>
                          </li>
                        ))}
                    </ul>
                  </div>
                ) : client.mails.length > 0 ? ("✅ All Read") : ("📭 No Mail History")}
              </td>
              <td style={tdStyle}>
                <button
                  onClick={() => window.open(`http://localhost:8000/download/${client["Client ID"]}`, "_blank")}
                  style={btnStyle}
                >📁 Download Zip</button>
                
                {/* THE "MARK ALL READ" BUTTON IS NOW DISABLED FOR THIS TEST */}
                {client.unread_count > 0 && (
                  <button style={{...btnStyle, cursor: 'not-allowed', backgroundColor: '#f0f0f0', color: '#aaa'}}>
                    ✅ Mark All Read (Disabled)
                  </button>
                )}

              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// All the style consts are the same
const thStyle = { padding: "10px", border: "1px solid #ccc", textAlign: "left" };
const tdStyle = { padding: "10px", border: "1px solid #ccc" };
const btnStyle = { padding: "6px 10px", marginRight: "6px", backgroundColor: "#e0e0e0", border: "none", borderRadius: "4px", cursor: "pointer" };
const viewBtnStyle = { padding: "2px 6px", marginLeft: "8px", backgroundColor: "#d1e7ff", border: "1px solid #a6cfff", borderRadius: "4px", cursor: "pointer", fontSize: "12px" };

export default ClientList;