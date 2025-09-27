package models

import (
	"time"
)

type RequestLogEntry struct {
	Timestamp     time.Time         `json:"timestamp"`
	CorrelationID string            `json:"correlation_id"`
	Method        string            `json:"method"`
	Path          string            `json:"path"`
	ServiceName   string            `json:"service_name,omitempty"`
	ClientIP      string            `json:"client_ip"`
	UserID        string            `json:"user_id,omitempty"`
	StatusCode    int               `json:"status_code"`
	Duration      time.Duration     `json:"duration"`
	RequestSize   int64             `json:"request_size"`
	ResponseSize  int64             `json:"response_size"`
	Error         string            `json:"error,omitempty"`
	Headers       map[string]string `json:"headers,omitempty"`
}

func NewRequestLogEntry(correlationID, method, path, clientIP string) *RequestLogEntry {
	return &RequestLogEntry{
		Timestamp:     time.Now(),
		CorrelationID: correlationID,
		Method:        method,
		Path:          path,
		ClientIP:      clientIP,
		Headers:       make(map[string]string),
	}
}

func (r *RequestLogEntry) SetResponse(statusCode int, duration time.Duration, responseSize int64) {
	r.StatusCode = statusCode
	r.Duration = duration
	r.ResponseSize = responseSize
}

func (r *RequestLogEntry) SetError(err string) {
	r.Error = err
}

func (r *RequestLogEntry) SetService(serviceName string) {
	r.ServiceName = serviceName
}

func (r *RequestLogEntry) SetUser(userID string) {
	r.UserID = userID
}

func (r *RequestLogEntry) AddHeader(key, value string) {
	if r.Headers == nil {
		r.Headers = make(map[string]string)
	}
	// Don't log sensitive headers
	if key != "Authorization" && key != "Cookie" {
		r.Headers[key] = value
	}
}