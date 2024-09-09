import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./App.tsx";
import Root from "./routes/root/page.tsx";
import { rootLoader } from "./routes/root/loader.ts";

import "./index.css";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    loader: rootLoader,
    // children: [
    //   {
    //     path: 'team',
    //     element: <Team />,
    //     loader: teamLoader,
    //   },
    // ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
