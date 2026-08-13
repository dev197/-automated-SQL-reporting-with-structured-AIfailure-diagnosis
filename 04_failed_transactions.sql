SELECT 
    COUNT(*) AS FailedOrderCount,
    SUM(TotalAmount) AS FailedOrderValue
FROM Orders
WHERE Status = 'Failed'
  AND OrderDate >= CAST(GETDATE() - 7 AS DATE);