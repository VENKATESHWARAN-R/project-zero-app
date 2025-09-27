package models

import (
	"time"
)

type CircuitState string

const (
	CircuitClosed   CircuitState = "closed"
	CircuitOpen     CircuitState = "open"
	CircuitHalfOpen CircuitState = "half_open"
)

type CircuitBreakerSettings struct {
	MaxRequests      uint32        `json:"max_requests" yaml:"max_requests"`
	Interval         time.Duration `json:"interval" yaml:"interval"`
	Timeout          time.Duration `json:"timeout" yaml:"timeout"`
	FailureThreshold float64       `json:"failure_threshold" yaml:"failure_threshold"`
}

type CircuitBreakerState struct {
	ServiceName  string                  `json:"service_name"`
	State        CircuitState            `json:"state"`
	FailureCount int                     `json:"failure_count"`
	SuccessCount int                     `json:"success_count"`
	LastFailure  time.Time               `json:"last_failure"`
	NextRetry    time.Time               `json:"next_retry"`
	Settings     CircuitBreakerSettings  `json:"settings"`
}

func NewCircuitBreakerSettings(maxRequests uint32, interval, timeout time.Duration, failureThreshold float64) *CircuitBreakerSettings {
	return &CircuitBreakerSettings{
		MaxRequests:      maxRequests,
		Interval:         interval,
		Timeout:          timeout,
		FailureThreshold: failureThreshold,
	}
}

func NewCircuitBreakerState(serviceName string, settings CircuitBreakerSettings) *CircuitBreakerState {
	return &CircuitBreakerState{
		ServiceName: serviceName,
		State:       CircuitClosed,
		Settings:    settings,
	}
}

func (c *CircuitBreakerState) CanRequest() bool {
	switch c.State {
	case CircuitClosed:
		return true
	case CircuitOpen:
		return time.Now().After(c.NextRetry)
	case CircuitHalfOpen:
		return c.SuccessCount < int(c.Settings.MaxRequests)
	default:
		return false
	}
}

func (c *CircuitBreakerState) RecordSuccess() {
	switch c.State {
	case CircuitClosed:
		c.FailureCount = 0
	case CircuitHalfOpen:
		c.SuccessCount++
		if c.SuccessCount >= int(c.Settings.MaxRequests) {
			c.State = CircuitClosed
			c.FailureCount = 0
			c.SuccessCount = 0
		}
	}
}

func (c *CircuitBreakerState) RecordFailure() {
	c.FailureCount++
	c.LastFailure = time.Now()

	switch c.State {
	case CircuitClosed:
		if c.shouldOpenCircuit() {
			c.State = CircuitOpen
			c.NextRetry = time.Now().Add(c.Settings.Timeout)
		}
	case CircuitHalfOpen:
		c.State = CircuitOpen
		c.NextRetry = time.Now().Add(c.Settings.Timeout)
		c.SuccessCount = 0
	}
}

func (c *CircuitBreakerState) shouldOpenCircuit() bool {
	totalRequests := c.FailureCount + c.SuccessCount
	if totalRequests < int(c.Settings.MaxRequests) {
		return false
	}

	failureRate := float64(c.FailureCount) / float64(totalRequests)
	return failureRate >= c.Settings.FailureThreshold
}