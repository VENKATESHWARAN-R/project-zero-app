class TemplateRenderer {
  static renderTemplate(template, variables) {
    if (!template || !template.content) {
      throw new Error('Template content is required');
    }

    let renderedContent = template.content;
    let renderedSubject = template.subject || '';

    // Replace variables in content
    renderedContent = this.replaceVariables(renderedContent, variables);

    // Replace variables in subject if it exists
    if (renderedSubject) {
      renderedSubject = this.replaceVariables(renderedSubject, variables);
    }

    return {
      subject: renderedSubject,
      content: renderedContent,
      channel: template.channel
    };
  }

  static replaceVariables(text, variables) {
    if (!text || !variables) {
      return text;
    }

    // Replace {{variableName}} patterns
    return text.replace(/\{\{(\w+)\}\}/g, (match, variableName) => {
      const value = this.getNestedValue(variables, variableName);
      return value !== undefined ? value : match; // Keep original if not found
    });
  }

  static getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  static validateTemplateVariables(template, variables) {
    const errors = [];

    if (!template.variables) {
      return errors; // No required variables defined
    }

    for (const [varName, varConfig] of Object.entries(template.variables)) {
      const value = this.getNestedValue(variables, varName);

      if (varConfig.required && (value === undefined || value === null || value === '')) {
        errors.push({
          variable: varName,
          message: `Required variable '${varName}' is missing`,
          type: 'missing_required'
        });
        continue;
      }

      if (value !== undefined && varConfig.type) {
        const actualType = Array.isArray(value) ? 'array' : typeof value;
        if (actualType !== varConfig.type) {
          errors.push({
            variable: varName,
            message: `Variable '${varName}' should be of type '${varConfig.type}' but got '${actualType}'`,
            type: 'type_mismatch',
            expected: varConfig.type,
            actual: actualType
          });
        }
      }

      if (value !== undefined && varConfig.pattern) {
        const regex = new RegExp(varConfig.pattern);
        if (!regex.test(String(value))) {
          errors.push({
            variable: varName,
            message: `Variable '${varName}' does not match required pattern: ${varConfig.pattern}`,
            type: 'pattern_mismatch',
            pattern: varConfig.pattern,
            value: String(value)
          });
        }
      }
    }

    return errors;
  }

  static extractVariablesFromTemplate(content) {
    const variableRegex = /\{\{(\w+(?:\.\w+)*)\}\}/g;
    const variables = new Set();
    let match;

    while ((match = variableRegex.exec(content)) !== null) {
      variables.add(match[1]);
    }

    return Array.from(variables);
  }

  static generateTemplatePreview(template, sampleVariables = {}) {
    try {
      // Create sample data for preview
      const variables = this.extractVariablesFromTemplate(template.content);
      const previewVariables = { ...sampleVariables };

      // Fill in missing variables with sample data
      variables.forEach(varName => {
        if (!(varName in previewVariables)) {
          previewVariables[varName] = `[${varName}]`;
        }
      });

      return this.renderTemplate(template, previewVariables);
    } catch (error) {
      throw new Error(`Failed to generate template preview: ${error.message}`);
    }
  }
}

module.exports = TemplateRenderer;