import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';

const Charts = ({ results }) => {
  const [classData, setClassData] = useState([]);
  
  useEffect(() => {
    if (results && results.summary && results.summary.class_counts) {
      // Convert class counts to array format for charts
      const data = Object.entries(results.summary.class_counts).map(([name, value]) => ({
        name,
        value
      }));
      
      // Sort by count (descending)
      data.sort((a, b) => b.value - a.value);
      
      // Take top 10 for cleaner charts
      setClassData(data.slice(0, 10));
    }
  }, [results]);
  
  // Return if no data
  if (!classData.length) {
    return null;
  }
  
  // Colors for pie chart
  const COLORS = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28DFF',
    '#FF6E76', '#58B8FF', '#83D178', '#FF9E9E', '#9B9B9B'
  ];
  
  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">Detection Analytics</h2>
      
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Object Distribution</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={classData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#0088FE" name="Count" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-3">Object Proportion</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={classData}
                cx="50%"
                cy="50%"
                outerRadius={120}
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
              >
                {classData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value} objects`, 'Count']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Charts;