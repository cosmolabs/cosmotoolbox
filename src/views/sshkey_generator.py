# Copyright (C) 2022 - 2025 Alessandro Iepure
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk, Adw, GObject, Gio, Gdk
from typing import List

# ToDo: update this service once you create the service for ssh keys
from ..services.sshkey_generator import SshKeyGeneratorService


@Gtk.Template(resource_path="/me/iepure/devtoolbox/ui/views/sshkey_generator.ui")
class SshKeyGeneratorView(Adw.Bin):
    __gtype_name__ = "SshKeyGeneratorView"

    # Template elements
    _toast = Gtk.Template.Child()
    _title = Gtk.Template.Child()
    _keytype_dropdown = Gtk.Template.Child()
    _keysize_dropdown = Gtk.Template.Child()
    _comment_entry  = Gtk.Template.Child()
    _password_entry = Gtk.Template.Child()
    _save_ssh_keys_switch = Gtk.Template.Child()
    _key_save_row = Gtk.Template.Child()
    _key_save_path = Gtk.Template.Child()
    _key_save_btn = Gtk.Template.Child()
    _generate_sshkeys_btn = Gtk.Template.Child()
    _public_key_area = Gtk.Template.Child()
    _private_key_area = Gtk.Template.Child()
    _service = SshKeyGeneratorService()

    # internal variables
    _keytype = ""
    _keysize = 0
    _saved_toast = Adw.Toast(
        priority=Adw.ToastPriority.HIGH, button_label=_("Open Folder"))


    def __init__(self):
        super().__init__()

        # Initial key save location visibility is false
        self._key_save_row.set_visible(False)
        self._key_save_path.set_visible(False)

        # Signals
        self._keytype_dropdown.connect("notify::selected", self._on_keytype_changed)
        self._keysize_dropdown.connect("notify::selected", self._on_keysize_changed)
        self._comment_entry.connect("changed", self._on_comment_entry_changed)
        self._password_entry.connect("changed", self._on_password_entry_changed)
        self._save_ssh_keys_switch.connect("notify::active", self._on_save_option_changed)
        self._key_save_btn.connect("clicked", self._on_key_save_clicked)
        self._generate_sshkeys_btn.connect("clicked", self._on_generate_keys_clicked)
        self._saved_toast.connect("button-clicked", self._on_toast_btn_clicked)


    # Functions to clear out the existing data when an attribute changes
    def _on_keytype_changed(self, pspec:GObject.ParamSpec, user_data:GObject.GPointer):
        self._public_key_area.clear()
        self._private_key_area.clear()
        self._keysize_update()

    def _keysize_update(self):
        if self._keytype_dropdown.get_selected() == 0  : #rsa
            self._keysize_dropdown.set_visible(True)
            keysize_values =Gtk.StringList()
            keysize_values.append("1024")
            keysize_values.append("2048")
            keysize_values.append("3072")
            keysize_values.append("4096")
            self._keysize_dropdown.set_model(keysize_values)
        elif self._keytype_dropdown.get_selected() == 1: #ed25519
            self._keysize_dropdown.set_visible(False)
        elif self._keytype_dropdown.get_selected() == 2: #rsa
            self._keysize_dropdown.set_visible(True)
            keysize_values =Gtk.StringList()
            keysize_values.append("256")
            keysize_values.append("384")
            keysize_values.append("521")
            self._keysize_dropdown.set_model(keysize_values)

    def _on_keysize_changed(self, pspec:GObject.ParamSpec, user_data:GObject.GPointer):
        self._public_key_area.clear()
        self._private_key_area.clear()

    def _on_comment_entry_changed(self, user_data:GObject.GPointer):
        self._public_key_area.clear()
        self._private_key_area.clear()

    def _on_password_entry_changed(self, user_data:GObject.GPointer):
        self._public_key_area.clear()
        self._private_key_area.clear()
    
    def _on_save_option_changed(self, pspec:GObject.ParamSpec, user_data:GObject.GPointer):
        if self._save_ssh_keys_switch.get_active():
            self._key_save_row.set_visible(True)
        else:
            self._key_save_row.set_visible(False)
            self._key_save_path.set_label("")
    
    def _on_key_save_clicked(self, user_data: GObject.GPointer):
        app = Gio.Application.get_default()
        window = app.get_active_window()
        self._file_dialog = Gtk.FileDialog(
            modal=True,
            title=_("Please choose a folder"),
            accept_label=_("Select")
        )
        self._file_dialog.select_folder(window, None, self._on_select_folder_complete, None)

    def _on_select_folder_complete(self, source: GObject.Object, result: Gio.AsyncResult, user_data: List = None):
        selected_folder = source.select_folder_finish(result)
        self._key_save_path.set_label(selected_folder.peek_path())

    def _on_generate_keys_clicked(self, user_data: GObject.GPointer):
        if not self._field_checks():
            self._generate()

    def _field_checks(self):

        has_errors = False

        if (self._save_ssh_keys_switch.get_active() == 1 and len(self._key_save_path.get_label()) <= 0):
            self._key_save_row.add_css_class("border-red")
            has_errors = True

        return has_errors

    def _generate(self):

        # Stop previous tasks
        self._service.get_cancellable().cancel()

        # Setup
        # Key Type & Size Conversions
        match self._keytype_dropdown.get_selected():
            case 0: # RSA
                self._keytype = "rsa"
                if self._keysize_dropdown.get_selected() == 0:
                    self._keysize = 1024
                elif self._keysize_dropdown.get_selected() == 1:
                    self._keysize = 2048
                elif self._keysize_dropdown.get_selected() == 2:
                    self._keysize = 3072
                elif self._keysize_dropdown.get_selected() == 3:
                    self._keysize = 4096
            case 1: # ed25519
                self._keytype = "ed25519"
            case 2: # ecdsa
                self._keytype = "ecdsa"
                if self._keysize_dropdown.get_selected() == 0: #256
                    self._keysize = 256
                elif self._keysize_dropdown.get_selected() == 1: #384
                    self._keysize = 384
                elif self._keysize_dropdown.get_selected() == 2: #521
                    self._keysize = 521

        self._service.set_keytype(self._keytype)
        self._service.set_keysize(self._keysize)
        self._service.set_comment(self._comment_entry.get_text())
        self._service.set_password(self._password_entry.get_text())
        self._service.set_save_path(self._key_save_path.get_label())
         
        # Call task
        self._service.generate_async(self, self._on_generation_done)
        
        if self._save_ssh_keys_switch.get_active() == 1:
            self._saved_toast.set_title(("SSH key pair stored successfully."))
            self._toast.add_toast(self._saved_toast)

    def _on_generation_done(self, source_widget:GObject.Object, result:Gio.AsyncResult, user_data:GObject.GPointer):
        priv_key, pub_key = self._service.async_finish(result, self)
        self._public_key_area.set_text(pub_key)
        self._private_key_area.set_text(priv_key)


    def _on_toast_btn_clicked(self, user_data: GObject.GPointer):
        app = Gio.Application.get_default()
        window = app.get_active_window()
        Gtk.show_uri(window, "file://" + self._key_save_path.get_label(), Gdk.CURRENT_TIME)

