SELECT 
    c.Segment,
    SUM(o.TotalAmount) AS TotalRevenue,
    COUNT(o.OrderID) AS OrderCount,
    AVG(o.TotalAmount) AS AvgOrderValue
FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID
WHERE o.Status = 'Completed'
GROUP BY c.Segment
ORDER BY TotalRevenue DESC;
