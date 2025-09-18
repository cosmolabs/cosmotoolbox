
# Copyright (C) 2022 - 2025 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, GObject
from sshkey_tools.keys import (
    RsaPrivateKey,
    EcdsaPrivateKey,
    Ed25519PrivateKey,
    EcdsaCurves
)

class SshKeyGeneratorService():

    def __init__(self):
        self._cancellable = Gio.Cancellable()

    def set_keytype(self, keytype:int):
        self._keytype = keytype 

    
    def set_keysize(self, keysize:int):
        self._keysize = keysize 
    
    
    def set_comment(self, comment:str):
        self._comment = comment 
    
    
    def set_password(self, password:str):
        self._password = password
    
    def set_save_path(self, savepath:str):
        self._savepath = savepath
    

    def get_cancellable(self) -> Gio.Cancellable:
        return self._cancellable

    def async_finish(self, result:Gio.AsyncResult, caller:GObject.Object):
        if not Gio.Task.is_valid(result, caller):
            return -1
        self._keytype = None
        return result.propagate_value().value

    def generate_async(self, caller:GObject.Object, callback:callable):
        task = Gio.Task.new(caller, None, callback, self._cancellable)
        task.set_return_on_cancel(True)
        task.run_in_thread(self._generate_thread)

    def _generate_thread(self, task:Gio.Task, source_object:GObject.Object, task_data:object, cancelable:Gio.Cancellable):
        if task.return_error_if_cancelled():
            return
        outcome = self._generate(self._keytype, self._keysize, self._comment, self._password)
        task.return_value(outcome)

    def _generate(self, keytype:str, keysize:int, comment:str, password:str) -> (str, str):
        match keytype:
            case "rsa":
                rsa_priv = RsaPrivateKey.generate(keysize)
                rsa_pub = rsa_priv.public_key
                rsa_pub.comment = comment
                if len(password) > 0:
                    if len(self._savepath) > 0 :
                        rsa_priv.to_file(self._savepath + f"/rsa-{keysize}", password, "utf-8")
                        rsa_pub.to_file(self._savepath + f"/rsa-{keysize}.pub", "utf-8")
                    return rsa_priv.to_string(password), rsa_pub.to_string()
                else:
                    if len(self._savepath) > 0 :
                        rsa_priv.to_file(self._savepath + f"/rsa-{keysize}", None, "utf-8")
                        rsa_pub.to_file(self._savepath + f"/rsa-{keysize}.pub", "utf-8")
                    return rsa_priv.to_string(), rsa_pub.to_string()
            case "ed25519":
                ed25519_priv = Ed25519PrivateKey.generate()
                ed25519_pub = ed25519_priv.public_key
                ed25519_pub.comment = comment
                if len(password) > 0:
                    if len(self._savepath) > 0 :
                        ed25519_priv.to_file(self._savepath + "/ed25519", password, "utf-8")
                        ed25519_pub.to_file(self._savepath + "/ed25519.pub", "utf-8")
                    return ed25519_priv.to_string(password, "utf-8"), ed25519_pub.to_string("utf-8")
                else:
                    if len(self._savepath) > 0 :
                        ed25519_priv.to_file(self._savepath + "/ed25519", None, "utf-8")
                        ed25519_pub.to_file(self._savepath + "/ed25519.pub", "utf-8")
                    return ed25519_priv.to_string(None, "utf-8"), ed25519_pub.to_string("utf-8")
            case "ecdsa":
                if keysize == 256:
                    curvesize = EcdsaCurves.P256
                elif keysize == 384:
                    curvesize = EcdsaCurves.P384
                elif keysize == 521:
                    curvesize = EcdsaCurves.P521
                ecdsa_priv = EcdsaPrivateKey.generate(curvesize)
                ecdsa_pub = ecdsa_priv.public_key
                ecdsa_pub.comment = comment
                if len(password) > 0:
                    if len(self._savepath) > 0 :
                        ecdsa_priv.to_file(self._savepath + f"/ecdsa-{keysize}", password, "utf-8")
                        ecdsa_pub.to_file(self._savepath + f"/ecdsa-{keysize}.pub", "utf-8")
                    return ecdsa_priv.to_string(password, "utf-8"), ecdsa_pub.to_string("utf-8")
                else:
                    if len(self._savepath) > 0 :
                        ecdsa_priv.to_file(self._savepath + f"/ecdsa-{keysize}", None, "utf-8")
                        ecdsa_pub.to_file(self._savepath + f"/ecdsa-{keysize}.pub", "utf-8")
                    return ecdsa_priv.to_string(None,"utf-8"), ecdsa_pub.to_string("utf-8")
