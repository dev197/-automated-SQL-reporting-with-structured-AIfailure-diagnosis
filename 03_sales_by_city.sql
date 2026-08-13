--SELECT * FROM Customers
--SELECT * FROM Orders
--SELECT * FROM OrderDetails

SELECT TOP 10
	C.City,
	SUM(O.TotalAMount) AS Total_Sales,
	COUNT(O.OrderID) AS Order_Count
FROM Orders O
JOIN Customers AS C
ON O.CustomerID = C.CustomerID
JOIN OrderDetails AS OD
ON O.OrderID  = OD.OrderID
WHERE O.Status = 'Completed'
GROUP BY C.City
ORDER BY Total_Sales DESC
