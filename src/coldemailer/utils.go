package main

import (
	"encoding/base64"
	"fmt"
	"log"
	"net/mail"

	"google.golang.org/api/gmail/v1"
)

func (e *email) send(s *gmail.Service) {
	msg := gen(e)

	_, err := s.Users.Messages.Send("me", msg).Do()
	if err != nil {
		log.Printf("err %v", err)
	}
}

func gen(e *email) *gmail.Message {
	destFormal := e.DestName + " " + e.DestLast
	a := mail.Address{Name: senderName, Address: senderAddr}
	b := mail.Address{Name: destFormal, Address: e.DestAddr}
	s := a.String()

	header := make(map[string]string)
	header["From"] = s
	header["Reply-To"] = s
	header["To"] = b.String()
	header["Subject"] = subject
	header["MIME-Version"] = "1.0"
	header["Content-Type"] = "text/html; charset='UTF-8'"
	header["Content-Transfer-Encoding"] = "quoted-printable"

	c := ""
	m := ""

	for k, v := range header {
		c += fmt.Sprintf("%s: %s\r\n", k, v)
	}

	if e.DestFirm == destFormal {
		m = angel(e)
	} else {
		m = funds(e)
	}

	c += "\r\n" + m

	msg := gmail.Message{
		Raw: base64.RawURLEncoding.EncodeToString([]byte(c)),
	}

	return &msg
}
