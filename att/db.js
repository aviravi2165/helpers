// db.js
const sql = require("mssql");
const curDate = new Date();
const currentTable = `DeviceLogs_${curDate.getMonth() + 1}_${curDate.getFullYear()}`;
const config = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  server: process.env.DB_SERVER,
  database: process.env.DB_NAME,
  table: currentTable,
  port: parseInt(process.env.DB_PORT || "1433", 10),
  options: {
    encrypt: false,
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

async function stampLog(code) {
  const pool = await getPool();
  const qry = `
  INSERT INTO ${config.table} (
      DownloadDate,
      DeviceId,
      UserId,
      LogDate,
      Direction,
      AttDirection,
      StatusCode,
      WorkCode,
      VerificationMode,
      IsApproved,
      LogRecordLocation,
      AttenndanceMarkingType,
      Lattitude,
      Longitude,
      NetworkLattitude,
      Temperature,
      TemperatureState
  )
  VALUES (
      GETDATE(),
      '18',
      '${code}',
      DATEADD(SECOND, 38, GETDATE()),
      N'in',
      N' ',
      N'0',
      N'0',
      N'1004',
      1,
      N'',
      N'Biometric',
      N'',
      N'',
      N'',
      0.0,
      0
  );`;
  const result = await pool.request().query(qry);
  return result.rowsAffected[0] > 0;
}

module.exports = {
  sql,
  executeQuery,
  stampLog,
};
