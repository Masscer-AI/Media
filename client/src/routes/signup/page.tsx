import React, { useState } from "react";
import axios from "axios";
import { Toaster, toast } from "react-hot-toast";
import "./styles.css";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const [message, setMessage] = useState("");

  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const endpoint = isLogin ? "/login/" : "/signup/";
    const payload = isLogin
      ? { email, password }
      : { username, email, password };
    try {
      const response = await axios.post(endpoint, payload);
      setMessage(response.data.message);
      if (!isLogin) {
        toast.success("User created successfully!");
      }
      else {
        toast.success("Succesfully logged in!")

      }
      navigate("/chat")
    } catch (error) {
      setMessage(error.response?.data?.detail || "An error occurred");
      toast.error("An error occurred");
    }
  };

  return (
    <div className="signup-component">
      <Toaster />
      <SimpleForm>
        <h2 className="simple-form-title">{isLogin ? "Login" : "Signup"}</h2>
        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <div className="simple-form-group">
              <label className="simple-form-label">Username:</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required={!isLogin}
                className="simple-form-input"
              />
            </div>
          )}
          <div className="simple-form-group">
            <label className="simple-form-label">Email:</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="simple-form-input"
            />
          </div>
          <div className="simple-form-group">
            <label className="simple-form-label">Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="simple-form-input"
            />
          </div>
          <button type="submit" className="simple-form-button">
            {isLogin ? "Login" : "Signup"}
          </button>
        </form>
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="simple-form-button"
        >
          {isLogin ? "Switch to Signup" : "Switch to Login"}
        </button>
      </SimpleForm>
    </div>
  );
}

const SimpleForm = ({ children }) => {
  return <div className="simple-form">{children}</div>;
};
