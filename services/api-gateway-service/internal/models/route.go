package models

type RouteConfig struct {
	Path         string            `json:"path" yaml:"path" mapstructure:"path" validate:"required"`
	Method       string            `json:"method" yaml:"method" mapstructure:"method"`
	ServiceName  string            `json:"service_name" yaml:"service_name" mapstructure:"service_name" validate:"required"`
	StripPrefix  bool              `json:"strip_prefix" yaml:"strip_prefix" mapstructure:"strip_prefix"`
	Headers      map[string]string `json:"headers,omitempty" yaml:"headers,omitempty" mapstructure:"headers"`
	AuthRequired bool              `json:"auth_required" yaml:"auth_required" mapstructure:"auth_required"`
}

func NewRouteConfig(path, serviceName string) *RouteConfig {
	return &RouteConfig{
		Path:        path,
		Method:      "*", // Default to all methods
		ServiceName: serviceName,
		Headers:     make(map[string]string),
	}
}

func (r *RouteConfig) Matches(method, path string) bool {
	// Simple prefix matching for now
	// TODO: Implement more sophisticated pattern matching
	if r.Method != "*" && r.Method != method {
		return false
	}

	// Remove trailing /* for matching
	routePath := r.Path
	if len(routePath) > 2 && routePath[len(routePath)-2:] == "/*" {
		routePath = routePath[:len(routePath)-2]
	}

	// Check if the request path starts with the route path
	if len(path) >= len(routePath) {
		return path[:len(routePath)] == routePath
	}

	return false
}

func (r *RouteConfig) ExtractProxyPath(requestPath string) string {
	if !r.StripPrefix {
		return requestPath
	}

	// Remove the route path prefix
	routePath := r.Path
	if len(routePath) > 2 && routePath[len(routePath)-2:] == "/*" {
		routePath = routePath[:len(routePath)-2]
	}

	if len(requestPath) > len(routePath) {
		return requestPath[len(routePath):]
	}

	return "/"
}