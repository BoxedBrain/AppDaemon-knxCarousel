# coding: utf8

# Import Home Assistant plugin & Jinja2
import appdaemon.plugins.hass.hassapi as hass
import jinja2

# Define Jinja2 environment
jenv = jinja2.Environment()

# Define the AppDaemon plugin class
class KnxCarousel(hass.Hass):
  def initialize(self):
    self.handle_list = [] # List to store handles for recurring timers
    self.tick = 0 # Counter for tracking the current tick

    # -------------------- INIT ARGS --------------------
    if not 'debug'        in self.args: self.args['debug'] = False
    if not 'debug_level'  in self.args: self.args['debug_level'] = "DEBUG"
    if not 'ascii_encode' in self.args: self.args['ascii_encode'] = True

    self.delay            = self.args.get('delay', 5)   # Delay between ticks
    self.default_address  = self.args.get('address', None) # Default KNX address
    self.default_dpt      = self.args.get('dpt', '16.001')     # Default KNX data point type
    self.default_truncate = self.args.get("truncate", 14) # Default truncate telegrams at 14 bytes 
    self.objects          = self.args.get('objects', []) # List of objects to send to KNX bus


    # -------------------- VALIDATE ARGS --------------------
    if not isinstance(self.delay, (int, float)):
      raise TypeError("delay must be a number (int or float).")
    if self.delay < 0:
      raise ValueError("delay cannot be negative.")

    if not isinstance(self.default_truncate, int):
      raise TypeError("truncate must be of type integer.")
    if self.delay < 0:
      raise ValueError("truncate cannot be negative.")


    # -------------------- START TICKS ---------------------
    self.handle_list.append(
        self.run_every(self.work, self.datetime(), self.delay)
    )


  def work(self, kwargs):
    # Reset tick counter if it exceeds the number of objects
    if (self.tick > (len(self.objects)-1)): self.tick = 0

    # Get the current object from the objects list
    obj = self.objects[self.tick]
    # Get the key of the current object
    nxt = list(obj)[0]

    # Handle different object types
    match nxt:
      case 'text': # Static 'text' object type
        payload = obj['text']

      case 'datetime': # Current 'datetime' object type
        now = self.datetime()
        payload = now.strftime(obj['datetime'])

      case 'entity': # Home Assistant 'entity' object type
        entity = self.get_entity(obj['entity'])
        
        if 'attribute' in obj.keys(): 
          payload = entity.get_state(attribute=obj['attribute'])
        else:
          payload = entity.get_state()

      case _:
        # Raise a ValueError for unknown object types
        raise ValueError("Unknown object '{}'".format(nxt))

    if not 'format'   in obj.keys(): obj['format']   = "{{ payload }}"
    if not 'address'  in obj.keys(): obj['address']  = self.default_address
    if not 'dpt'      in obj.keys(): obj['dpt']      = self.default_dpt
    if not 'truncate' in obj.keys(): obj['truncate'] = self.default_truncate

    pld = jenv.from_string(obj['format'])
    payload = pld.render(payload = payload)

    if type(obj['address']) is list:
      for addr in obj['address']:
        self.knx_send(str(payload), str(addr), str(obj['dpt']), int(obj['truncate']))
    else:
      self.knx_send(str(payload), str(obj['address']), str(obj['dpt']), int(obj['truncate']))
    
    self.tick += 1


  def knx_send(self, payload, address, dpt, truncate, *args, **kwargs):
    if payload is None and not isinstance(payload, str):
      raise TypeError("payload argument must be defined and of type string!")

    if address is None and not isinstance(address, str):
      raise TypeError("address argument must defined and be of type string!")
    
    if dpt is None and not isinstance(dpt, str):
      raise TypeError("dpt argument must be defined and of type string!")

    if truncate is not None and not isinstance(truncate, int):
      raise TypeError("truncate argument must be of type integer!")

    if truncate:
      payload = payload[:truncate]

    self.debug("[KNX msg] '{payload}' to '{address}' DPT: {dpt}".format(payload = payload, address = address, dpt= dpt))
    self.call_service("knx/send", address=address, payload=payload, type=dpt)


  def debug(self, message):
    if self.args['debug']:
      self.log('{message}'.format(message = message), ascii_encode = False, level = self.args["debug_level"])


def terminate(self):
  for handle in self.handle_list:
      self.cancel_timer(handle)