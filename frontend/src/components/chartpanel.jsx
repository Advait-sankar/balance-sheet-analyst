import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ChartPanel({ data }) {
  const chartData = [
    { name: "Revenue", value: data.revenue_from_operations },
    { name: "Assets", value: data.total_assets },
    { name: "Liabilities", value: data.total_liabilities },
    { name: "Cash", value: data.cash_and_cash_equivalents },
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-6">
      <h2 className="text-xl font-semibold mb-4">Company Financial Overview</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
