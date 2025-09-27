package models

import (
	"time"
)

type LimitScope string

const (
	ScopeGlobal  LimitScope = "global"
	ScopePerIP   LimitScope = "per_ip"
	ScopePerUser LimitScope = "per_user"
)

type RateLimitPolicy struct {
	Name     string        `json:"name" yaml:"name" validate:"required"`
	Requests int           `json:"requests" yaml:"requests" validate:"required,min=1"`
	Window   time.Duration `json:"window" yaml:"window" validate:"required"`
	Burst    int           `json:"burst" yaml:"burst" validate:"required,min=1"`
	Scope    LimitScope    `json:"scope" yaml:"scope"`
	Enabled  bool          `json:"enabled" yaml:"enabled"`
}

func NewRateLimitPolicy(name string, requests int, window time.Duration, burst int) *RateLimitPolicy {
	return &RateLimitPolicy{
		Name:     name,
		Requests: requests,
		Window:   window,
		Burst:    burst,
		Scope:    ScopePerIP,
		Enabled:  true,
	}
}

func (r *RateLimitPolicy) GetRate() float64 {
	return float64(r.Requests) / r.Window.Seconds()
}

func (r *RateLimitPolicy) IsValid() bool {
	return r.Requests > 0 && r.Window > 0 && r.Burst >= r.Requests
}