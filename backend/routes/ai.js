const express = require("express");
const Groq = require("groq-sdk");

const router = express.Router();

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

router.post("/chat", async (req, res) => {
  try {
    const { prompt } = req.body;

    const completion = await groq.chat.completions.create({
      messages: [
        {
          role: "user",
          content: prompt,
        },
      ],
      model: "llama3-8b-8192",
    });

    res.json({
      response: completion.choices[0]?.message?.content || "No response",
    });
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: "Groq API failed" });
  }
});

module.exports = router;