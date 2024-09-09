// src/routes/root.tsx
import { LoaderFunction } from 'react-router-dom';

export const rootLoader: LoaderFunction = async () => {
  const response = await fetch('https://jsonplaceholder.typicode.com/posts');
  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }
  const data = await response.json();
  return { posts: data };
};
