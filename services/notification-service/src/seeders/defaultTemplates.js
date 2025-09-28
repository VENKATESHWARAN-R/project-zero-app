const { NotificationTemplate } = require('../models');
const { v4: uuidv4 } = require('uuid');

const defaultTemplates = [
  {
    id: uuidv4(),
    name: 'welcome_email_registration',
    type: 'welcome',
    channel: 'email',
    subject: 'Welcome to Project Zero App, {{userName}}!',
    content: `Hello {{userName}},

Welcome to Project Zero App! We're excited to have you join our community.

To get started, please activate your account by clicking the link below:
{{activationLink}}

If you have any questions, feel free to reach out to our support team.

Best regards,
The Project Zero App Team`,
    variables: {
      userName: { type: 'string', required: true, description: 'User display name' },
      activationLink: { type: 'string', required: true, description: 'Account activation URL' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'order_email_confirmation',
    type: 'order',
    channel: 'email',
    subject: 'Order Confirmation - {{orderNumber}}',
    content: `Dear {{customerName}},

Thank you for your order! Here are the details:

Order Number: {{orderNumber}}
Total Amount: {{orderTotal}}

Items:
{{#each orderItems}}
- {{name}}: {{price}}
{{/each}}

Estimated Delivery: {{estimatedDelivery}}

You can track your order status in your account dashboard.

Thank you for choosing Project Zero App!

Best regards,
The Project Zero App Team`,
    variables: {
      customerName: { type: 'string', required: true, description: 'Customer name' },
      orderNumber: { type: 'string', required: true, description: 'Order number' },
      orderTotal: { type: 'string', required: true, description: 'Order total amount' },
      orderItems: { type: 'array', required: true, description: 'Array of order items' },
      estimatedDelivery: { type: 'string', required: true, description: 'Estimated delivery date' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'order_sms_shipped',
    type: 'order',
    channel: 'sms',
    subject: null,
    content: 'Good news! Your order {{orderNumber}} has shipped and will arrive by {{deliveryDate}}. Track: {{trackingNumber}}',
    variables: {
      orderNumber: { type: 'string', required: true, description: 'Order number' },
      deliveryDate: { type: 'string', required: true, description: 'Expected delivery date' },
      trackingNumber: { type: 'string', required: true, description: 'Shipping tracking number' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'payment_email_receipt',
    type: 'payment',
    channel: 'email',
    subject: 'Payment Receipt - {{amount}}',
    content: `Dear {{customerName}},

Your payment has been successfully processed.

Amount: {{amount}}
Order Number: {{orderNumber}}
Payment Method: Card ending in {{last4}}
Transaction ID: {{transactionId}}
Date: {{paymentDate}}

Thank you for your payment!

Best regards,
The Project Zero App Team`,
    variables: {
      customerName: { type: 'string', required: true, description: 'Customer name' },
      amount: { type: 'string', required: true, description: 'Payment amount' },
      orderNumber: { type: 'string', required: true, description: 'Order number' },
      last4: { type: 'string', required: true, description: 'Last 4 digits of payment card' },
      transactionId: { type: 'string', required: true, description: 'Payment transaction ID' },
      paymentDate: { type: 'string', required: true, description: 'Payment date' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'payment_sms_confirmation',
    type: 'payment',
    channel: 'sms',
    subject: null,
    content: 'Payment of {{amount}} for order {{orderNumber}} confirmed. Card ending {{last4}}. Thank you!',
    variables: {
      amount: { type: 'string', required: true, description: 'Payment amount' },
      orderNumber: { type: 'string', required: true, description: 'Order number' },
      last4: { type: 'string', required: true, description: 'Last 4 digits of payment card' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'system_in_app_maintenance',
    type: 'system',
    channel: 'in_app',
    subject: 'Scheduled Maintenance Notice',
    content: `Scheduled maintenance is planned for {{maintenanceDate}} from {{startTime}} to {{endTime}}.

During this time, {{affectedServices}} may be temporarily unavailable.

We apologize for any inconvenience and appreciate your patience.`,
    variables: {
      maintenanceDate: { type: 'string', required: true, description: 'Maintenance date' },
      startTime: { type: 'string', required: true, description: 'Maintenance start time' },
      endTime: { type: 'string', required: true, description: 'Maintenance end time' },
      affectedServices: { type: 'string', required: true, description: 'Services affected by maintenance' }
    },
    isActive: true
  },
  {
    id: uuidv4(),
    name: 'promotional_email_newsletter',
    type: 'promotional',
    channel: 'email',
    subject: '{{campaignTitle}} - Special Offer Inside!',
    content: `Hi {{customerName}},

{{campaignTitle}}

{{campaignContent}}

Use code {{promoCode}} to get {{discount}} off your next purchase!

Valid until {{expiryDate}}.

Shop now: {{shopLink}}

Best regards,
The Project Zero App Team

Unsubscribe: {{unsubscribeLink}}`,
    variables: {
      customerName: { type: 'string', required: true, description: 'Customer name' },
      campaignTitle: { type: 'string', required: true, description: 'Campaign title' },
      campaignContent: { type: 'string', required: true, description: 'Campaign content' },
      promoCode: { type: 'string', required: true, description: 'Promotional code' },
      discount: { type: 'string', required: true, description: 'Discount amount' },
      expiryDate: { type: 'string', required: true, description: 'Promotion expiry date' },
      shopLink: { type: 'string', required: true, description: 'Link to shop' },
      unsubscribeLink: { type: 'string', required: true, description: 'Unsubscribe link' }
    },
    isActive: true
  }
];

async function seedDefaultTemplates() {
  try {
    console.log('Starting to seed default notification templates...');

    for (const templateData of defaultTemplates) {
      // Check if template already exists
      const existingTemplate = await NotificationTemplate.findOne({
        where: { name: templateData.name }
      });

      if (!existingTemplate) {
        await NotificationTemplate.create(templateData);
        console.log(`Created template: ${templateData.name}`);
      } else {
        console.log(`Template already exists: ${templateData.name}`);
      }
    }

    console.log('Default templates seeding completed successfully!');
    return true;
  } catch (error) {
    console.error('Error seeding default templates:', error);
    throw error;
  }
}

module.exports = {
  defaultTemplates,
  seedDefaultTemplates
};