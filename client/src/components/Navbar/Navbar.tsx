import React from "react";
import "./navbar.css";

export const Navbar = () => {
  return (
    <nav className="navbar">
      <section className="nerko-one-regular">
        <h1>
          Let's Practice<strong>AI</strong>
        </h1>
      </section>
      <section>
        <span>Login</span>
        <span>Signup</span>
      </section>
    </nav>
  );
};
