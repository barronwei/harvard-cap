package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"golang.org/x/oauth2"
)

func genClient(c *oauth2.Config) *http.Client {
	f := "token.json"
	t, err := tokenFromLoc(f)
	if err != nil {
		save(f, tokenFromWeb(c))
	}

	return c.Client(context.Background(), t)
}

func tokenFromLoc(loc string) (*oauth2.Token, error) {
	f, err := os.Open(loc)
	if err != nil {
		return nil, err
	}

	defer f.Close()

	tok := new(oauth2.Token)
	err = json.NewDecoder(f).Decode(tok)
	return tok, err
}

func tokenFromWeb(c *oauth2.Config) *oauth2.Token {
	ln := c.AuthCodeURL("state-token", oauth2.AccessTypeOffline)
	fmt.Printf("Go this link to obtain auth access: \n%v\n", ln)

	secret := new(string)
	_, err := fmt.Scan(secret)
	if err != nil {
		log.Fatalf("Unable to read the auth code: %v", err)
	}

	t, err := c.Exchange(context.TODO(), *secret)
	if err != nil {
		log.Fatalf("Unable to get token from web: %v", err)
	}

	return t
}

func save(path string, t *oauth2.Token) {
	fmt.Printf("Saving credential file to: %s\n", path)

	f, err := os.OpenFile(path, os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		log.Fatalf("Unable to cache auth token: %v", err)
	}

	defer f.Close()

	json.NewEncoder(f).Encode(t)
}
