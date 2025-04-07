import flet as ft
from models.models import Pad
from ui.dialogs import confirm_delete_dialog


def create_pad_ui(
    index: int,
    pad: Pad,
    state: dict,
    handlers: dict,
    refs: dict
) -> ft.Container:
    page = refs["page"]
    pad_refs = refs["pad_refs"]
    audio_players = refs["audio_players"]
    file_picker = refs["file_picker"]
    confirm_dialog_state = state["confirm_dialog_state"]
    selected_pad_index = state["selected_pad_index"]
    sd_path = state["sd_path"]

    pad_ref = ft.Ref[ft.Container]()

    def handle_close(e):
        page.close(dlg_delete)

    def confirm_delete(e):
        delete_pad(e)
        handle_close(e)

    def delete_pad(e):
        if pad.is_occupied or getattr(pad, "special_marker", False):
            pad.file_path = None
            pad.is_playing = False
            pad.special_marker = False
            if index in audio_players:
                audio_players.pop(index)
            handlers["refresh_pads"]()

    def toggle_play_stop():
        if not pad.file_path or not pad.file_path.exists() or getattr(pad, "special_marker", False):
            return

        if pad.is_playing:
            player = audio_players.get(index)
            if player:
                player.pause()
            pad.is_playing = False
        else:
            player = ft.Audio(src=str(pad.file_path), autoplay=True)
            audio_players[index] = player
            page.overlay.append(player)
            page.update()
            pad.is_playing = True

        handlers["refresh_pads"]()

    def on_click(e):
        if getattr(pad, "special_marker", False):
            return

        if not sd_path["path"]:
            page.open(
                ft.SnackBar(
                    ft.Text(
                        "Карта памяти не выбрана",
                        font_family="VT323",
                        size=18,
                        color=ft.Colors.WHITE
                    ),
                    bgcolor=ft.Colors.RED_900
                )
            )
            return

        if not pad.is_occupied:
            selected_pad_index["index"] = index
            file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["wav", "mp3", "flac", "ogg", "aiff", "m4a"]
            )
        else:
            toggle_play_stop()

    def on_long_press(e):
        if confirm_dialog_state["show"] is False:
            delete_pad(e)
        elif pad.is_occupied or getattr(pad, "special_marker", False):
            page.open(dlg_delete)
            page.update()

    dlg_delete = confirm_delete_dialog(
        on_confirm_with_event=confirm_delete,
        on_cancel_with_event=handle_close,
        on_checkbox_change=lambda e: confirm_dialog_state.update({"show": not e.control.value})
    )

    tooltip = str(pad.file_path.name) if pad.is_occupied else ""
    bgcolor = ft.Colors.ORANGE_900 if getattr(pad, "special_marker", False) \
        else ft.Colors.RED_500 if pad.is_playing \
        else ft.Colors.RED_700 if pad.is_occupied \
        else ft.Colors.GREY_400

    shadow = ft.BoxShadow(
        spread_radius=3, blur_radius=8, color=ft.Colors.RED_400, offset=ft.Offset(0, 0)
    ) if pad.is_playing else None

    container = ft.Container(
        ref=pad_ref,
        content=ft.Text(str(pad.pad_id), size=32, color=ft.Colors.BLACK, font_family="Orbitron"),
        width=80,
        height=80,
        bgcolor=bgcolor,
        alignment=ft.alignment.center,
        border_radius=5,
        shadow=shadow,
        on_click=on_click,
        on_long_press=on_long_press,
        tooltip=tooltip,
    )

    pad_refs.append(pad_ref)

    return container