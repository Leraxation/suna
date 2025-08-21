// frontend/src/pages/create-website.js
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function CreateWebsite() {
  const [siteConfig, setSiteConfig] = useState({ title: '', theme: 'light' });

  const handleSubmit = async () => {
    // API call to backend for website generation
    const response = await fetch('http://localhost:8000/api/create-website', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(siteConfig),
    });
    const data = await response.json();
    console.log('Website created:', data);
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h1>Create Website</h1>
      <input
        type="text"
        placeholder="Website Title"
        onChange={(e) => setSiteConfig({ ...siteConfig, title: e.target.value })}
      />
      <button onClick={handleSubmit}>Generate Website</button>
    </motion.div>
  );
}