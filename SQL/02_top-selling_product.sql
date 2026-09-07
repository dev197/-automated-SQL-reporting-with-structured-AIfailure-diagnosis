--select * from OrderDetails
--select * from Products

SELECT TOP 5
    p.ProductName,
    SUM(od.Quantity) AS TotalUnitsSold,
    SUM(od.Quantity * od.UnitPrice) AS TotalRevenue
FROM OrderDetails od
JOIN Products p ON od.ProductID = p.ProductID
JOIN Orders o ON od.OrderID = o.OrderID
WHERE o.Status = 'Completed'
GROUP BY p.ProductName
ORDER BY TotalUnitsSold DESC;
