// db.js
const sql = require("mssql");

const config = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER, // e.g. 'localhost'
  database: process.env.DB_NAME,
  port: parseInt(process.env.DB_PORT || "1433", 10),
  options: {
    encrypt: false, // set true if using Azure or TLS
    trustServerCertificate: true,
  },
};

let pool;

async function getPool() {
  if (pool) return pool;
  pool = await sql.connect(config);
  return pool;
}

async function executeQuery(queryText) {
  const pool = await getPool();
  const result = await pool.request().query(queryText);
  return result.recordset;
}

module.exports = {
  sql,
  executeQuery,
};
