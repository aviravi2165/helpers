SELECT 
	tm.docCode,
	um1.firstName + ' ' + um1.lastName AS 'Task To',
	um1.phoneNumber AS 'Task To Contact',
	um2.firstName + ' ' + um2.lastName AS 'Task By',
	um2.phoneNumber AS 'Task By Contact',
	tm.taskDetails,
	tm.deadline
FROM 
	taskMgmt tm
INNER JOIN usersMaster um1 ON tm.taskTo = um1.userId
INNER JOIN deptMaster dm1 ON um1.deptId = dm1.id
INNER JOIN usersMaster um2 ON tm.taskTo = um2.userId
INNER JOIN deptMaster dm2 ON um2.deptId = dm2.id
WHERE 
	tm.acceptanceStatus <> 'REJECTED'
	AND
	tm.acknowledgeStatus = 0
