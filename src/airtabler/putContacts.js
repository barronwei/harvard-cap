const sweep = require('../sweeper.json')

const c = {
  fields: ['VC Firm or Angel Name'],
  cellFormat: 'json',
  filterByFormula: '{Investor Type}="Individual Angel"'
}

const putContacts = b => {
  b('Investor Contact Status')
    .select(c)
    .firstPage((e, data) => {
      if (e) {
        console.error(e)
      } else {
        const temp = data.map(d => d.fields['VC Firm or Angel Name'])

        const f = Object.keys(sweep)
          .filter(ks => !temp.includes(ks))
          .reduce((o, ks) => {
            return {
              ...o,
              [ks]: sweep[ks]
            }
          }, {})

        const k = Object.keys(f)
        const v = k.map(ks => f[ks])

        const r = k.map((ks, i) => {
          const name = ks.split(' ').reverse()
          const [lst, ...fst] = name

          return {
            fields: {
              'VC Firm or Angel Name': ks,
              Status: 'To Reach Out To',
              'Contact First Name': fst.reverse().join(' '),
              'Contact Last Name': lst,
              Email: v[i],
              'Investor Type': 'Individual Angel'
            }
          }
        })

        let res = []

        while (r.length) {
          let a = r.splice(0, 10)
          res.push(a)
        }

        res.forEach(arr => {
          b('Investor Contact Status').create(arr, (e, ref) => {
            if (e) {
              console.error(e)
            } else {
              ref.forEach(x => {
                console.log(x.getId())
              })
            }
          })
        })
      }
    })
}

module.exports = putContacts
