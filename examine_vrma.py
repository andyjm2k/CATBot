import json
import struct

def examine_vrma_file(filename):
    """Examine the structure of a VRMA file to understand its format."""
    try:
        with open(filename, 'rb') as f:
            # Read first 100 bytes to see if it's a valid GLTF/VRMA
            header = f.read(100)
            print('First 100 bytes:', header[:50])

            # Check if it's a GLB file (binary glTF)
            if header.startswith(b'glTF'):
                print('This appears to be a GLB file')
            else:
                print('This does not appear to be a standard GLB file')

            # Try to read as JSON (VRMA might be JSON format)
            f.seek(0)
            try:
                content = f.read()
                json_content = content.decode('utf-8')
                parsed = json.loads(json_content)
                print('Successfully parsed as JSON')
                print('Keys:', list(parsed.keys()) if isinstance(parsed, dict) else 'Not a dict')

                if 'vrmAnimations' in parsed:
                    print('Found vrmAnimations')
                    if parsed['vrmAnimations']:
                        anim = parsed['vrmAnimations'][0]
                        print('Animation keys:', list(anim.keys()) if isinstance(anim, dict) else 'Not a dict')
                        if 'humanoidTracks' in anim:
                            tracks = anim['humanoidTracks']
                            print('HumanoidTracks type:', type(tracks))
                            print('HumanoidTracks length:', len(tracks) if hasattr(tracks, '__len__') else 'No length')
                            if hasattr(tracks, '__len__') and len(tracks) > 0:
                                print('First track keys:', list(tracks[0].keys()) if isinstance(tracks[0], dict) else 'Not a dict')
                else:
                    print('No vrmAnimations found in root')

            except UnicodeDecodeError:
                print('Cannot decode as UTF-8')
            except json.JSONDecodeError:
                print('Not valid JSON')

    except Exception as e:
        print(f'Error examining file: {e}')

if __name__ == "__main__":
    examine_vrma_file('model_avatar/Eva/Kawaii Kaiwai.vrma')
