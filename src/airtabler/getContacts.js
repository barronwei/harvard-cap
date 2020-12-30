const sys = require('fs')

const c = {
  fields: [
    'VC Firm or Angel Name',
    'Contact First Name',
    'Contact Last Name',
    'Email'
  ],
  cellFormat: 'json',
  filterByFormula:
    'AND({HUCP Contact}="Barron Wei", {Status}="To Reach Out To")'
}

const getContacts = b => {
  b('Investor Contact Status')
    .select(c)
    .firstPage((e, data) => {
      if (e) {
        console.error(e)
      } else {
        if (data.length) {
          data.forEach(d =>
            b('Investor Contact Status').update([
              {
                id: d.id,
                fields: {
                  Status: 'Sent Initial Email'
                }
              }
            ])
          )

          const temp = data.map(d => d.fields)
          const dump = temp.map(d => {
            return {
              destFirm: d['VC Firm or Angel Name'],
              destName: d['Contact First Name'],
              destLast: d['Contact Last Name'],
              destAddr: d['Email']
            }
          })

          sys.writeFile('../../coldemailer.json', JSON.stringify(dump), e => {
            e ? console.error(e) : console.log('Saved!')
          })
        } else {
          console.log('There is no one to send out to!')
        }
      }
    })
}

module.exports = getContacts
