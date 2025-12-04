import importlib
import logging

log = logging.getLogger(__name__)


class schemaLoader:
    @staticmethod
    def coerceRPC(module_name, cls, msg):
        obj = cls()
        obj.cmd = msg.get("cmd")
        obj.agentId = msg.get("agentId")
        errs = []
        for attr in obj.keys():
            typ_info = getattr(cls, attr).info.get("type")
            if isinstance(typ_info, list):
                for clsname in [c.__title__ for c in typ_info]:
                    TypClass = getattr(importlib.import_module(module_name), clsname)
                    obj_attr = getattr(obj, attr)
                    try:
                        obj_attr = TypClass(**msg.get(attr))
                        obj_attr.validate()
                        setattr(obj, attr, obj_attr)
                        break
                    except Exception as e:
                        errs.append(str(e))
                        log.debug(f"Coercion error: {e}")
                        continue
                if not getattr(obj, attr):
                    errstr = '\n'.join(errs)
                    raise Exception(f"Could not coerce message to known RPC class, logged errors:\n{errstr}")
        return obj
