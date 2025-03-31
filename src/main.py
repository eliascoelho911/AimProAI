import random
import flet as ft
import time
import threading


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "TheEthicalVideo"
    page.window.always_on_top = True
    page.spacing = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variable to control the timer loop
    timer_active = True
    timer = None
    is_playing = False
    slider_being_dragged = False  # Flag to track if user is dragging the slider

    def handle_volume_change(e):
        video.volume = e.control.value
        page.update()
        print(f"Video.volume = {e.control.value}")

    def handle_playback_rate_change(e):
        video.playback_rate = e.control.value
        page.update()
        print(f"Video.playback_rate = {e.control.value}")

    def update_video_progress_bar(e=None):
        nonlocal timer_active, timer
        
        if not timer_active:
            return
            
        current_position = video.get_current_position() or 0
        total_duration = video.get_duration() or 1  # Avoid division by zero
        
        # Update the progress bar value only if the slider is not being dragged
        if total_duration > 0 and not slider_being_dragged:
            progress_slider.value = current_position / total_duration
            
        # Update time labels
        update_time_display(current_position)
        
        # Check if video is completed
        if video.is_completed():
            handle_play_pause(None)  # Pause the video and timer
        
        # Schedule next update using threading.Timer (faster refresh rate)
        if not slider_being_dragged:
            progress_slider.update()
            time_display.update()
        
        if timer_active:
            timer = threading.Timer(0.2, update_video_progress_bar)  # Update 5 times per second
            timer.start()
    
    def update_time_display(current_position):
        # Update time labels
        total_duration = video.get_duration() or 1
        current_time = format_time(current_position)
        total_time = format_time(total_duration)
        time_display.value = f"{current_time} / {total_time}"
    
    def format_time(milliseconds):
        seconds = int(milliseconds / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def handle_slider_change(e):
        nonlocal slider_being_dragged
        slider_being_dragged = True
        
        # Update time display while dragging
        total_duration = video.get_duration() or 1
        current_position = int(e.control.value * total_duration)
        update_time_display(current_position)
        time_display.update()
        
    def handle_progress_change_end(e):
        nonlocal slider_being_dragged
        # Reset the flag when slider interaction ends
        slider_being_dragged = False
        
        # Quando o usuário solta o slider, busca a posição no vídeo
        total_duration = video.get_duration() or 1
        target_position = int(e.control.value * total_duration)
        
        # Seek to the new position
        video.seek(target_position)
        print(f"Video.seek({target_position})")
        
        # Update time labels immediately
        update_time_display(target_position)
        
        # Update the UI
        page.update()
    
    def handle_play_pause(e):
        nonlocal timer_active, timer, is_playing
        
        if is_playing:
            # If playing, pause the video
            video.pause()
            timer_active = False
            if timer:
                timer.cancel()
            play_pause_button.icon = ft.icons.PLAY_ARROW
            is_playing = False
        else:
            # If paused, play the video
            video.play()
            timer_active = True
            update_video_progress_bar()  # Start updating the progress bar
            play_pause_button.icon = ft.icons.PAUSE
            is_playing = True
        
        page.update()
        print(f"Video {'paused' if not is_playing else 'playing'}")
    
    # Clean up when closing the app
    def on_close(e):
        nonlocal timer_active, timer
        timer_active = False
        if timer:
            timer.cancel()
        
    page.on_close = on_close

    sample_media = [
        ft.VideoMedia(
            "src/assets/videos/example_01.mp4"
        ),
    ]

    # Create time display text
    time_display = ft.Text("00:00 / 00:00", size=14)
    
    # Create progress slider instead of progress bar
    progress_slider = ft.Slider(
        value=0,
        min=0,
        max=1,
        divisions=100,
        width=400,
        height=20,
        on_change=handle_slider_change,
        on_change_end=handle_progress_change_end,
    )
    
    # Create play/pause button
    play_pause_button = ft.IconButton(
        icon=ft.icons.PLAY_ARROW,
        icon_size=30,
        on_click=handle_play_pause,
    )
    
    # Video control buttons row
    video_controls = ft.Row(
        [play_pause_button],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Video progress control container
    video_progress_control = ft.Container(
        content=ft.Column([
            progress_slider,
            ft.Row(
                [time_display, video_controls],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=400,
            ),
        ], 
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=10
    )

    page.add(
        video := ft.Video(
            expand=True,
            playlist=sample_media,
            playlist_mode=ft.PlaylistMode.LOOP,
            fill_color=ft.Colors.BLUE_400,
            aspect_ratio=16/9,
            volume=100,
            autoplay=False,
            filter_quality=ft.FilterQuality.HIGH,
            muted=False,
            on_loaded=lambda e: print("Video loaded successfully!"),
            on_enter_fullscreen=lambda e: print("Video entered fullscreen!"),
            on_exit_fullscreen=lambda e: print("Video exited fullscreen!"),
        ),
        video_progress_control,
        ft.Slider(
            min=0,
            value=100,
            max=100,
            label="Volume = {value}%",
            divisions=10,
            width=400,
            on_change=handle_volume_change,
        ),
        ft.Slider(
            min=1,
            value=1,
            max=3,
            label="PlaybackRate = {value}X",
            divisions=6,
            width=400,
            on_change=handle_playback_rate_change,
        ),
    )
    
    # Start progress bar update when the app loads
    # but don't activate the timer since the video starts paused
    timer_active = False
    
    # Initialize time display
    update_time_display(0)


ft.app(main)