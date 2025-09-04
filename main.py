import asyncio
import logging
import argparse
from ruuvitag_sensor.ruuvi import RuuviTagSensor
from asyncua import Server, ua

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

def get_friendly_name(mac):
    return mac.replace(":", "")[:4]

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="RuuviServer")
    parser.add_argument("--uri", default="http://examples.freeopcua.github.io")
    args = parser.parse_args()

    # OPC UA Server setup
    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:4840/{args.name}/server/")
    server.set_server_name(args.name)
    server.historizing = True # Enable historizing
    
    # Setup our own namespace
    uri = args.uri
    idx = await server.register_namespace(uri)

    # Create a folder for RuuviTags
    ruuvi_tags_folder = await server.nodes.objects.add_folder(idx, "RuuviTags")

    _logger.info("Starting server!")
    async with server:
        while True:
            async for data in RuuviTagSensor.get_data_async():
                mac = data[0]
                sensor_data = data[1]
                friendly_name = get_friendly_name(mac)

                # Check if the RuuviTag object already exists
                ruuvi_tag_object = None
                for child in await ruuvi_tags_folder.get_children():
                    if await child.read_browse_name() == ua.QualifiedName(friendly_name, idx):
                        ruuvi_tag_object = child
                        break
                
                # If the object doesn't exist, create it
                if ruuvi_tag_object is None:
                    ruuvi_tag_object = await ruuvi_tags_folder.add_object(ua.NodeId(friendly_name, idx), ua.QualifiedName(friendly_name, idx))

                    temp_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.Temperature", idx), ua.QualifiedName(f"{friendly_name}.Temperature", idx), 0.0)
                    await temp_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await temp_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    humidity_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.Humidity", idx), ua.QualifiedName(f"{friendly_name}.Humidity", idx), 0.0)
                    await humidity_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await humidity_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    pressure_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.Pressure", idx), ua.QualifiedName(f"{friendly_name}.Pressure", idx), 0.0)
                    await pressure_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await pressure_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    accel_x_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.AccelerationX", idx), ua.QualifiedName(f"{friendly_name}.AccelerationX", idx), 0, ua.VariantType.Int64)
                    await accel_x_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await accel_x_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    accel_y_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.AccelerationY", idx), ua.QualifiedName(f"{friendly_name}.AccelerationY", idx), 0, ua.VariantType.Int64)
                    await accel_y_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await accel_y_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    accel_z_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.AccelerationZ", idx), ua.QualifiedName(f"{friendly_name}.AccelerationZ", idx), 0, ua.VariantType.Int64)
                    await accel_z_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await accel_z_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    voltage_var = await ruuvi_tag_object.add_property(ua.NodeId(f"{friendly_name}.BatteryVoltage", idx), ua.QualifiedName(f"{friendly_name}.BatteryVoltage", idx), 0, ua.VariantType.Int64)
                    await voltage_var.write_attribute(ua.AttributeIds.AccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))
                    await voltage_var.write_attribute(ua.AttributeIds.UserAccessLevel, ua.DataValue(ua.Variant(ua.AccessLevel.CurrentRead | ua.AccessLevel.HistoryRead, ua.VariantType.Byte)))

                    _logger.info(f"Created OPC UA object {ua.NodeId(friendly_name, idx)}")

                # Update the OPC UA variables and log the data
                temp_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.Temperature", idx))
                humidity_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.Humidity", idx))
                pressure_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.Pressure", idx))
                accel_x_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.AccelerationX", idx))
                accel_y_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.AccelerationY", idx))
                accel_z_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.AccelerationZ", idx))
                voltage_var = await ruuvi_tag_object.get_child(ua.QualifiedName(f"{friendly_name}.BatteryVoltage", idx))

                temp_val = sensor_data.get('temperature')
                humidity_val = sensor_data.get('humidity')
                pressure_val = sensor_data.get('pressure')
                accel_x_val = sensor_data.get('acceleration_x')
                accel_y_val = sensor_data.get('acceleration_y')
                accel_z_val = sensor_data.get('acceleration_z')
                voltage_val = sensor_data.get('battery')

                await temp_var.write_value(temp_val)
                await humidity_var.write_value(humidity_val)
                await pressure_var.write_value(pressure_val)
                await accel_x_var.write_value(accel_x_val)
                await accel_y_var.write_value(accel_y_val)
                await accel_z_var.write_value(accel_z_val)
                await voltage_var.write_value(voltage_val)

                _logger.info(f"Served data for {friendly_name}: Temp={temp_val}, Humidity={humidity_val}, Pressure={pressure_val}, AccelX={accel_x_val}, AccelY={accel_y_val}, AccelZ={accel_z_val}, Voltage={voltage_val}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass