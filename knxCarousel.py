# coding: utf8

# Import Home Assistant plugin
import appdaemon.plugins.hass.hassapi as hass

class KnxCarousel(hass.Hass):
  def initialize(self):
    self.handle_list = [] # List to store handles for recurring timers
    self.tick = 0 # Counter for tracking the current tick

    # -------------------- INIT ARGS --------------------
    if not 'debug'        in self.args: self.args['debug'] = False
    if not 'debug_level'  in self.args: self.args['debug_level'] = "DEBUG"
    if not 'ascii_encode' in self.args: self.args['ascii_encode'] = True

    self.delay           = self.args['delay']   # Delay between ticks
    self.default_address = self.args['address'] # Default KNX address
    self.default_dpt     = self.args['dpt']     # Default KNX data point type
    self.objects         = self.args['objects'] # List of objects to send to KNX bus


    # -------------------- VALIDATE ARGS --------------------
    if not isinstance(self.delay, (int, float)):
      raise TypeError("delay must be a number (int or float).")
    if self.delay < 0:
      raise ValueError("delay cannot be negative.")


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
            payload = entity.get_state()
            if 'attribute' in obj.keys(): payload = entity.get_state(attribute=obj['attribute'])

        case _:
            # Raise a ValueError for unknown object types
            raise ValueError("unknown object '{}'".format(nxt))

    if not 'format'  in obj.keys(): obj['format']  = "{}"
    if not 'address' in obj.keys(): obj['address'] = self.default_address
    if not 'dpt'     in obj.keys(): obj['dpt']     = self.default_dpt
    payload = obj['format'].format(payload)

    if type(obj['address']) is list:
      for addr in obj['address']:
        self.knx_send(str(payload), str(addr), str(obj['dpt']))
    else:
      self.knx_send(str(payload), str(obj['address']), str(obj['dpt']))
    
    self.tick += 1


  def knx_send(self, payload, address, dpt):

    if payload is not None and not isinstance(payload, str):
        raise TypeError("payload must be a string.")

    if address is not None and not isinstance(address, str):
        raise TypeError("address must be a string.")
    
    if dpt is not None and not isinstance(dpt, str):
        raise TypeError("dpt must be a string.")

    self.debug("[KNX msg] '{payload}' to '{address}' DPT: {dpt}".format(payload = payload, address = address, dpt= dpt))
    self.call_service("knx/send", address=address, payload=payload, type=dpt)


  def debug(self, message):
    if self.args['debug']:
        self.log('{message}'.format(message = message), ascii_encode = False, level = self.args["debug_level"])
        #self.call_service('notify/notify', title = 'Debug', message = text)


def terminate(self):
  for handle in self.handle_list:
      self.cancel_timer(handle)