package main

import (
	"database/sql"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
	"github.com/labstack/gommon/log"
	_ "github.com/lib/pq"
)

type Config struct {
	Keys []string
}

type State struct {
	Temperature float32
	Humidity    float32
}

var db *sql.DB

func init() {
	connStr := os.Getenv("DB_SRC")
	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}

}

func main() {
	fmt.Println("Version: 1.0")

	e := echo.New()
	e.Logger.SetLevel(log.INFO)

	var config Config
	_, err := toml.DecodeFile("config/config.toml", &config)
	if err != nil {
		e.Logger.Fatal(err)
	}
	e.Logger.Infof("Config: %v", config)

	auth := middleware.KeyAuth(func(key string, context echo.Context) (bool, error) {
		for _, k := range config.Keys {
			if k == key {
				return true, nil
			}
		}
		return false, nil
	})

	insertStmt, err := db.Prepare("INSERT INTO dht22 (time, temperature, humidity, location) VALUES( $1, $2, $3, $4)")
	if err != nil {
		log.Fatal(err)
	}

	e.POST("/upload", func(c echo.Context) error {
		humidity, err := strconv.ParseFloat(c.FormValue("humidity"), 32)
		if err != nil {
			return echo.NewHTTPError(http.StatusNotAcceptable)
		}
		temperature, err := strconv.ParseFloat(c.FormValue("temperature"), 32)
		if err != nil {
			return echo.NewHTTPError(http.StatusNotAcceptable)
		}
		t, err := strconv.ParseInt(c.FormValue("timestamp"), 10, 64)
		if err != nil {
			return echo.NewHTTPError(http.StatusNotAcceptable)
		}
		fmt.Println("time: ", t)
		timestamp := time.Unix(0, t*int64(time.Millisecond))
		location := c.FormValue("location")
		fmt.Println(timestamp, humidity, temperature, location)

		_, err = insertStmt.Exec(timestamp, temperature, humidity, location)
		if err != nil {
			log.Warnf("Failed to update DB: %v\n", err)
		}
		return c.String(http.StatusOK, "")
	}, auth)

	e.Logger.Fatal(e.Start(":1323"))
}
