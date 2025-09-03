# Ruuvi OPC UA Server

This project reads RuuviTag Bluetooth Low Energy (BLE) measurements and publishes them as an OPC UA server.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/ruuvi-opc.git
   cd ruuvi-opc
   ```

2. **Install dependencies using uv:**

   ```bash
   uv init
   uv sync
   ```

## Running the Server

To run the OPC UA server, execute the following command:

```bash
uv run main.py
```

The server will start and begin listening for RuuviTag advertisements. When a RuuviTag is discovered, it will be added to the OPC UA server's address space under the `RuuviTags` folder.

## Connecting a Client

To connect to the OPC UA server, you can use any OPC UA client. Here are the connection details:

*   **Endpoint URL:** `opc.tcp://<your-ip-address>:4840/ruuvi/server/`

Replace `<your-ip-address>` with the IP address of the machine running the server.

### Example using UaExpert

1.  **Download and install UaExpert:** [https://www.unified-automation.com/products/development-tools/uaexpert.html](https://www.unified-automation.com/products/development-tools/uaexpert.html)

2.  **Add a new server:**

    *   Click the `+` button to add a new server.
    *   In the `Add Server` dialog, enter the Endpoint URL in the `Server Uri` field.
    *   Click `OK`.

3.  **Connect to the server:**

    *   Select the server you just added from the list.
    *   Click the `Connect` button.

4.  **Browse the address space:**

    *   Once connected, you can browse the server's address space in the `Address Space` window.
    *   You will find the RuuviTags under the `RuuviTags` folder.

### Creating a Trend View in UaExpert

To visualize the sensor data over time, you can create a trend view in UaExpert:

1.  **Add a new document:**

    *   Click the `+` button in the `Documents` panel.
    *   Select `Trend View` from the list.

2.  **Add variables to the trend view:**

    *   Drag and drop the variables you want to monitor (e.g., `Temperature`, `Humidity`, `Pressure`) from the `Address Space` window into the trend view.

3.  **Start the trend:**

    *   The trend view will automatically start plotting the data as it is received from the server.

You can now see the sensor readings from your RuuviTags plotted in real-time.