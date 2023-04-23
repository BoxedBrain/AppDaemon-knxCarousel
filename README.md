# 🎠KNX Carousel AppDaemon Plugin

KNX Carousel is a custom AppDaemon/Home Assistant plugin that allows you to send different types of objects to the KNX bus at regular intervals. It supports various object types with customizable formatting options. This README provides instructions on how to properly configure the plugin.

## 🛠️ Prerequisites

Before you can use the KNX Carousel plugin, you need to have the following:

1. Home Assistant installation: Make sure you have Home Assistant installed and running on your system.

2. AppDaemon: KNX Carousel plugin uses AppDaemon, which is a separate service that runs alongside Home Assistant. You need to have AppDaemon installed and configured in your Home Assistant installation.

3. KNX integration: You need to have the KNX integration set up in your Home Assistant installation, and have the necessary KNX devices and addresses configured.

## ⚙️ Installation

To install the KNX Carousel plugin, follow these steps:

1. Inside the AppDaemon app directory, create a new directory called `knxCarousel` (or any other name you prefer).

2. Copy the provided `knxCarousel.py` file into the knxCarousel directory.

3. Create in the same folder a file called `knxCarousel.yaml`, add the following basic configuration to enable the KNX Carousel plugin:

```yaml
knxCarousel:
  module: knxCarousel
  class: KnxCarousel
  address: "1/2/3"
  dpt: "16.001"
  delay: 30
  objects:
    - text: Hello World!
```

## 🔧 Configuration

The KNX Carousel plugin is configured using the `knxCarousel.yaml` file. You can customize various settings to suit your needs. Here's an overview of the available configuration options:

```yaml
glastaster_office: # Replace with a unique name for your instance
  module: knxCarousel
  class: KnxCarousel

  # Default KNX address to send payloads to
  # Single address or list if needed
  address:
    - "1/2/3"
    - "2/3/4"
  dpt: "16.001" # Default KNX data point type to use

  delay: 5 # Delay in seconds between sending objects

  objects: # List of objects to send
    - text: World # Static text object type

      # All objects allow for custom formatting
      # Format using curly braces {}
      # This renders to "Hello World!"
      format: "Hello {}!"


    - datetime: "%d.%m.%Y" # Current datetime object type

      # All objects allow for individual DPT configuration
      dpt: "16.001"

    - entity: weather.forecast_home # Home Assistant entity 
      attribute: temperature # Optional attribute of the entity to retrieve
      format: "Temp: {}°C"

      # All objects allow for individual target address configuration
      address: "3/2/1"

  debug: True # Enable or disable debug mode
  debug_level: INFO # Debug level (INFO or DEBUG)
  ascii_encode: False # Enable or disable ASCII encoding for log messages
```

## 🗨️ Contributing

We welcome contributions to improve the functionality, performance, and usability of this plugin. If you are interested in contributing, please follow the guidelines below:

- Fork the repository and create a new branch for your contribution.
- Make your changes and ensure that the code passes all existing tests.
- Create a pull request with a clear description of your changes and why they are beneficial.
- Your contribution will be reviewed by the project maintainers and feedback may be provided for further improvements.
- Once your contribution is accepted, it will be merged into the main branch.

We appreciate any contributions. Thank you for helping to make this plugin even better! 🚀