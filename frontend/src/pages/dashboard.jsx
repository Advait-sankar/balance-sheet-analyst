import { useEffect, useState } from "react";
import axios from "axios";
import ChartPanel from "../components/ChartPanel";
import ChatBox from "../components/ChatBox";

export default function Dashboard({ user, onLogout }) {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1 className="text-3xl font-bold mb-4">Welcome, {user.name}</h1>
      <p>Your role: {user.role}</p>
      <button
        onClick={onLogout}
        className="bg-red-500 text-white px-4 py-2 rounded mt-4"
      >
        Logout
      </button>
    </div>
  );
}

