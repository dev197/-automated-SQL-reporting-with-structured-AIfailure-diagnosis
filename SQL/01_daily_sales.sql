SELECT 
    SUM(TotalAmount) AS TotalSales,
    COUNT(*) AS OrderCount
FROM Orders
WHERE OrderDate = CAST(GETDATE() - 1 AS DATE)
  AND Status = 'Completed';
