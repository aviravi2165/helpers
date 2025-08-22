use ievo;

DECLARE @StartDateRange1 DATE = '2025-08-12';
DECLARE @EndDateRange2 DATE = '2025-08-12'; 

-- Create dynamic labels
DECLARE @Label1 NVARCHAR(100) = FORMAT(@StartDateRange1, 'dd MMM') + ' - ' + FORMAT(@EndDateRange2, 'dd MMM');

-- Final Query
SELECT
    t.Label,
	t.Assignee,
	t.Department,
    COUNT(*) AS TotalTasks,

    SUM(CASE WHEN t.acceptanceStatus = 'PENDING' THEN 1 ELSE 0 END) AS PendingTasks,
    SUM(CASE WHEN t.acceptanceStatus = 'ACCEPTED' AND t.doneStatus = 0 AND t.acknowledgeStatus = 0 THEN 1 ELSE 0 END) AS AcceptedTasks,
    SUM(CASE WHEN t.acceptanceStatus = 'REJECTED' THEN 1 ELSE 0 END) AS RejectedTasks,

    SUM(CASE WHEN t.doneStatus = 1 AND t.acknowledgeStatus = 0 THEN 1 ELSE 0 END) AS DoneTasks,
    SUM(CASE WHEN t.acknowledgeStatus = 1 THEN 1 ELSE 0 END) AS AcknowledgedTasks,

    SUM(CASE WHEN t.acceptanceStatus = 'PENDING' AND CAST(t.deadline AS Date) < CAST(GETDATE() AS Date) THEN 1 ELSE 0 END) AS DeadlinePassedPendingAcceptance,
    SUM(CASE WHEN t.acceptanceStatus = 'ACCEPTED' AND t.doneStatus = 0 AND CAST(t.deadline AS Date) < CAST(GETDATE() AS Date) AND t.acceptanceStatus <> 'REJECTED' THEN 1 ELSE 0 END) AS DeadlinePassedNotPendingCompletion,
    SUM(CASE WHEN t.acceptanceStatus = 'ACCEPTED' AND t.doneStatus = 1 AND t.acknowledgeStatus = 0 AND CAST(t.deadline AS Date) < CAST(GETDATE() AS Date)  AND t.acceptanceStatus <> 'REJECTED' THEN 1 ELSE 0 END) AS DeadlinePassedPendingAcknowledgement,
    
    SUM(CASE WHEN t.acceptanceStatus = 'ACCEPTED' AND CAST(t.acceptanceOn AS Date) > CAST(t.deadline AS Date) THEN 1 ELSE 0 END) AS AcceptedAfterDeadline,
    SUM(CASE WHEN t.doneStatus = 1 AND CAST(t.doneOn  AS Date) > CAST(t.deadline AS Date) THEN 1 ELSE 0 END) AS DoneAfterDeadline,
	SUM(CASE WHEN t.acknowledgeStatus = 1 AND CAST(t.acknowledgeOn AS Date) > CAST(t.deadline AS Date) THEN 1 ELSE 0 END) AS AcknowledgedAfterDeadline

FROM (
    -- First range: Start to T-1
    SELECT 
    	tm.*, 
    	@Label1 AS Label, 
    	um.firstName + ' ' + um.lastName AS Assignee,
    	dm.subDept AS Department
    FROM taskMgmt tm
    INNER JOIN usersMaster um ON tm.taskTo = um.userId
    INNER JOIN deptMaster dm ON um.deptId = dm.id
    WHERE 
    	taskByOn BETWEEN @StartDateRange1 AND DATEADD(DAY, 1, @EndDateRange2)
    	AND
    	subDocId <> 1
    	AND
    	taskBy <> taskTo

) AS t
GROUP BY  t.Label, t.Assignee,t.Department
ORDER BY t.Department;

