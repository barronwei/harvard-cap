package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"golang.org/x/oauth2/google"
	"google.golang.org/api/gmail/v1"
)

func main() {
	c, err := ioutil.ReadFile("credentials.json")
	if err != nil {
		log.Fatalf("Unable to read credentials: %v", err)
	}

	config, err := google.ConfigFromJSON(c, gmail.GmailSendScope)
	if err != nil {
		log.Fatalf("Unable to parse the secret to config: %v", err)
	}

	client := genClient(config)

	s, err := gmail.New(client)
	if err != nil {
		log.Fatalf("Unable to find client: %v", err)
	}

	d, err := ioutil.ReadFile("coldemailer.json")
	if err != nil {
		log.Fatalf("Unable to load tables: %v", err)
	}

	tasks := new(emails)
	err = json.Unmarshal(d, tasks)
	if err != nil {
		log.Fatalf("Unable to parse tasks: %v", err)
	}

	for _, e := range *tasks {
		e.send(s)
	}

	fmt.Println("Done!")
}
