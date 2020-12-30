const env = require('dotenv')
const air = require('airtable')
const getContacts = require('./getContacts')
const putContacts = require('./putContacts')

const _ = env.config()
const b = new air({ apiKey: process.env.API_KEY }).base(process.env.BASE_ID)

const run = b => {
  switch (process.env.MODE) {
    case 'GET':
      getContacts(b)
      break
    case 'PUT':
      putContacts(b)
      break

    default:
      console.error('Please provide a mode!')
  }
}

run(b)
