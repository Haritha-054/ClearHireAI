require('dotenv').config()
const express = require('express')
const cors = require('cors')
const path = require('path')
const axios = require('axios')
const uploadRouter = require('./routes/upload')

const app = express()
const PORT = process.env.PORT || 5000

const aiRoutes = require("./routes/ai");
app.use("/api/ai", aiRoutes);

// Middleware
app.use(cors({
  origin: '*',
  credentials: true,
}))
app.use(express.json())

// Routes
app.use('/api/upload', uploadRouter)

// New Evaluation Endpoint
app.post('/api/evaluate', async (req, res) => {

  try {

    console.log("REQ BODY:", req.body)

    const response = await axios.post(
      'https://clearhireai-1.onrender.com/api/evaluate',
      req.body,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 120000,
      }
    )

    console.log("ML RESPONSE:", response.data)

    return res.json(response.data)

  } catch (error) {

    console.error(
      'Evaluation proxy error:',
      error.response?.data || error.message
    )

    return res.status(500).json({
      error:
        error.response?.data ||
        error.message ||
        'Evaluation failed'
    })
  }
})

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Why Did You Reject Me? — Backend',
    timestamp: new Date().toISOString(),
  })
})

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' })
})

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err)
  res.status(500).json({ error: err.message || 'Internal server error' })
})

app.listen(PORT, () => {
  console.log(`\n🚀 Backend running at http://localhost:${PORT}`)
  console.log(`   ML Service expected at http://localhost:8000`)
  console.log(`   Health check: http://localhost:${PORT}/api/health\n`)
})
