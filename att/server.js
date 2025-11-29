// server.js
require("dotenv").config();
const express = require("express");
const path = require("path");

const openModule = require("open");
const open = openModule.default || openModule; // <-- add this wrapper

const { executeQuery } = require("./db");
const app = express();
const PORT = process.env.PORT || 3000;

// Parse JSON bodies
app.use(express.json());

// Serve static files from /public (for the UI page)
app.use(express.static(path.join(__dirname, "public")));

// API endpoint to run arbitrary SQL query
app.post("/api/query", async (req, res) => {
  const { query } = req.body;

  if (!query || typeof query !== "string") {
    return res.status(400).json({ error: "Query is required." });
  }

  try {
    const result = await executeQuery(query);

    // Return raw result so you can see everything
    res.json(result);
  } catch (err) {
    console.error("SQL error:", err);
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  const url = `http://localhost:${PORT}`;
  console.log(`Server is running at ${url}`);

  // Try to open the UI page automatically in the default browser
  open(url).catch(() => {
    console.log("Please open the URL manually in your browser.");
  });
});
