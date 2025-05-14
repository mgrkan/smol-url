<script lang="ts">
    import { Input } from "$lib/components/ui/input";
    import { Card, CardContent } from "$lib/components/ui/card";
    import { Button } from "$lib/components/ui/button";
    import { Label } from "$lib/components/ui/label";

    let url = "";

    function handleSubmit() {
        // TODO: Handle URL submission
        console.log("Submitted URL:", url);
    }
</script>

<div class="min-h-screen flex items-center justify-center bg-background">
    <Card class="w-full max-w-md mx-4">
        <CardContent class="pt-6">
            <form on:submit|preventDefault={handleSubmit} class="space-y-4">
                <div class="space-y-2">
                    <Label for="url">Enter URL to shorten</Label>
                    <Input
                        id="url"
                        type="url"
                        bind:value={url}
                        placeholder="https://example.com/very/long/url"
                        class="w-full"
                    />
                </div>
                <Button type="submit" class="w-full">
                    Shorten URL
                </Button>
            </form>
        </CardContent>
    </Card>
</div>

<style>
    /* Add any custom styles here */
</style>
